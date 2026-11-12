#!/usr/bin/env python3
"""Rig the supplied unskinned Character 03 GLB; preserve source mesh and images.
Requires Python 3.10+ and NumPy. Output is a development artifact pending license review.
"""
from __future__ import annotations
import argparse, hashlib, json, math, struct
from pathlib import Path
import numpy as np

BONES = [
 ("pelvis",None,(0,-.08,0),.23),("spine","pelvis",(0,.15,0),.22),
 ("chest","spine",(0,.39,0),.22),("neck","chest",(0,.64,0),.14),
 ("head","neck",(0,.82,0),.20),("clavicle_L","chest",(-.14,.47,0),.14),
 ("upperarm_L","clavicle_L",(-.29,.40,0),.13),("forearm_L","upperarm_L",(-.43,.28,0),.12),
 ("hand_L","forearm_L",(-.51,.25,0),.10),("clavicle_R","chest",(.14,.47,0),.14),
 ("upperarm_R","clavicle_R",(.29,.40,0),.13),("forearm_R","upperarm_R",(.43,.28,0),.12),
 ("hand_R","forearm_R",(.51,.25,0),.10),("thigh_L","pelvis",(-.13,-.43,0),.18),
 ("shin_L","thigh_L",(-.14,-.79,0),.14),("foot_L","shin_L",(-.14,-.94,.03),.13),
 ("toe_L","foot_L",(-.14,-.96,.17),.11),("thigh_R","pelvis",(.13,-.43,0),.18),
 ("shin_R","thigh_R",(.14,-.79,0),.14),("foot_R","shin_R",(.14,-.94,.03),.13),
 ("toe_R","foot_R",(.14,-.96,.17),.11)]
BI={b[0]:i for i,b in enumerate(BONES)}
COMP={5123:2,5126:4}

def parse_glb(blob):
 if blob[:4]!=b"glTF": raise ValueError("Not a GLB")
 _,ver,total=struct.unpack_from("<4sII",blob,0)
 if ver!=2 or total!=len(blob): raise ValueError("Invalid GLB 2.0 container")
 p=12; chunks=[]
 while p<len(blob):
  n,k=struct.unpack_from("<II",blob,p);p+=8;chunks.append((k,blob[p:p+n]));p+=n
 d=json.loads(chunks[0][1].decode().rstrip("\0 "));b=bytearray(next((v for k,v in chunks if k==0x004E4942),b""))
 return d,b

def pack_glb(d,b):
 while len(b)%4:b.append(0)
 d["buffers"][0]["byteLength"]=len(b);j=json.dumps(d,separators=(",",":"),ensure_ascii=False).encode();j+=b" "*((-len(j))%4);bb=bytes(b)
 return struct.pack("<4sII",b"glTF",2,12+8+len(j)+8+len(bb))+struct.pack("<II",len(j),0x4E4F534A)+j+struct.pack("<II",len(bb),0x004E4942)+bb

def view(d,b,payload,target=None):
 while len(b)%4:b.append(0)
 off=len(b);b.extend(payload);v={"buffer":0,"byteOffset":off,"byteLength":len(payload)}
 if target:v["target"]=target
 d.setdefault("bufferViews",[]).append(v);return len(d["bufferViews"])-1

def accessor(d,v,ct,count,typ):
 d.setdefault("accessors",[]).append({"bufferView":v,"componentType":ct,"count":int(count),"type":typ});return len(d["accessors"])-1

def read_accessor(d,b,i):
 a=d["accessors"][i];v=d["bufferViews"][a["bufferView"]];n={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4,"MAT4":16}[a["type"]];ct=a["componentType"];size=COMP[ct];stride=v.get("byteStride",n*size);off=v.get("byteOffset",0)+a.get("byteOffset",0);dt="<u2" if ct==5123 else "<f4"
 if stride==n*size:return np.frombuffer(b,dtype=dt,count=a["count"]*n,offset=off).reshape(a["count"],n).copy()
 out=np.empty((a["count"],n),dtype=dt)
 for j in range(n):out[:,j]=np.ndarray((a["count"],),dtype=dt,buffer=b,offset=off+j*size,strides=(stride,))
 return out

def skin_weights(pos):
 parent_pos={n:np.asarray(p,np.float32) for n,_,p,_ in BONES};caps=[]
 for name,parent,p,sigma in BONES:
  end=np.asarray(p,np.float32);start=parent_pos[parent] if parent else np.array((0,-.99,0),np.float32);ab=end-start;caps.append((start,ab,float(ab@ab) or 1e-8,sigma,BI[name]))
 ji=np.empty((len(pos),4),np.uint16);we=np.empty((len(pos),4),np.float32);boneids=np.asarray([c[4] for c in caps],np.uint16)
 for st in range(0,len(pos),24000):
  p=pos[st:st+24000];score=np.empty((len(p),len(caps)),np.float32)
  for j,(a,ab,den,sigma,_) in enumerate(caps):
   t=np.clip(((p-a)@ab)/den,0,1);delta=p-(a+t[:,None]*ab);score[:,j]=np.exp(-.5*np.einsum("ij,ij->i",delta,delta)/(sigma*sigma))
  ids=np.argpartition(score,-4,axis=1)[:,-4:];vals=np.take_along_axis(score,ids,axis=1);sums=vals.sum(axis=1,keepdims=True)
  bad=sums[:,0]<1e-20
  if np.any(bad):
   best=np.argmax(score[bad],axis=1);ids[bad]=best[:,None];vals[bad]=0;vals[bad,0]=1;sums[bad]=1
  vals/=sums;order=np.argsort(-vals,axis=1);ids=np.take_along_axis(ids,order,axis=1);vals=np.take_along_axis(vals,order,axis=1)
  ji[st:st+len(p)]=boneids[ids];we[st:st+len(p)]=vals
 return ji,we

def qxyz(e):
 x,y,z=e;cx,sx=math.cos(x/2),math.sin(x/2);cy,sy=math.cos(y/2),math.sin(y/2);cz,sz=math.cos(z/2),math.sin(z/2)
 return (sx*cy*cz-cx*sy*sz,cx*sy*cz+sx*cy*sz,cx*cy*sz-sx*sy*cz,cx*cy*cz+sx*sy*sz)

def clips():
 out=[]
 def add(n,t,c,loop=True):out.append((n,t,c,loop))
 add("Idle",[0,1,2],{"spine":[(0,0,0),(.015,0,0),(0,0,0)],"chest":[(0,0,0),(0,0,.018),(0,0,0)],"head":[(0,0,0),(0,.035,0),(0,0,0)]})
 t=[0,.2,.4,.6,.8,1,1.2];ph=[2*math.pi*x/1.2 for x in t];c={}
 for side,sgn in [("L",1),("R",-1)]:
  v=[math.sin(x)*.48*sgn for x in ph];c[f"thigh_{side}"]=[(x,0,0) for x in v];c[f"shin_{side}"]=[(max(0,-x*sgn)*.62,0,0) for x in v];c[f"foot_{side}"]=[(-max(0,x*sgn)*.22,0,0) for x in v];c[f"upperarm_{side}"]=[(-math.sin(x)*.30*sgn,0,0) for x in ph];c[f"forearm_{side}"]=[(max(0,math.sin(x)*sgn)*.12,0,0) for x in ph]
 c.update({"spine":[(-.025,0,0)]*7,"chest":[(0,0,0)]*7});add("Walk",t,c)
 t=[0,.1,.2,.3,.4,.5,.6,.7];ph=[2*math.pi*x/.7 for x in t];c={}
 for side,sgn in [("L",1),("R",-1)]:
  v=[math.sin(x)*.72*sgn for x in ph];c[f"thigh_{side}"]=[(x,0,0) for x in v];c[f"shin_{side}"]=[(max(0,-x*sgn)*1.05,0,0) for x in v];c[f"foot_{side}"]=[(-max(0,x*sgn)*.32,0,0) for x in v];c[f"upperarm_{side}"]=[(-math.sin(x)*.58*sgn,0,0) for x in ph];c[f"forearm_{side}"]=[(max(0,math.sin(x)*sgn)*.18,0,0) for x in ph]
 c.update({"spine":[(-.14,0,0)]*8,"chest":[(-.035,0,0)]*8});add("Run",t,c)
 add("Crouch",[0,1],{"thigh_L":[(-.68,0,0)]*2,"thigh_R":[(-.68,0,0)]*2,"shin_L":[(1.22,0,0)]*2,"shin_R":[(1.22,0,0)]*2,"foot_L":[(-.42,0,0)]*2,"foot_R":[(-.42,0,0)]*2,"spine":[(-.20,0,0)]*2,"chest":[(-.08,0,0)]*2,"upperarm_L":[(-.32,.55,0)]*2,"upperarm_R":[(-.32,-.55,0)]*2,"forearm_L":[(.38,0,0)]*2,"forearm_R":[(.38,0,0)]*2})
 t=[0,.35,.7,1.05,1.4];c={"upperarm_L":[(0,.78,0)]*5,"upperarm_R":[(0,-.78,0)]*5,"forearm_L":[(0,0,.78)]*5,"forearm_R":[(0,0,-.78)]*5,"thigh_L":[(0,0,-.12)]*5,"thigh_R":[(0,0,.12)]*5,"spine":[(-.10,0,0)]*5,"head":[(0,0,0),(0,.025,0),(0,0,0),(0,-.025,0),(0,0,0)]};add("Fight",t,c)
 t=[0,.12,.24,.38,.52,.68,.84];c={"upperarm_R":[(0,-.72,0),(0,-.72,0),(0,-1.22,0),(0,-1.35,0),(0,-.95,0),(0,-.72,0),(0,-.72,0)],"forearm_R":[(0,0,-.72),(0,0,-.72),(0,0,-.45),(0,0,-.12),(0,0,-.42),(0,0,-.72),(0,0,-.72)],"upperarm_L":[(0,.78,0)]*7,"forearm_L":[(0,0,.78)]*7,"spine":[(-.08,0,0),(-.12,0,0),(-.18,0,0),(-.13,.18,0),(-.10,.10,0),(-.08,0,0),(-.08,0,0)],"chest":[(0,0,0),(0,0,0),(0,.10,0),(0,.18,0),(0,.08,0),(0,0,0),(0,0,0)],"thigh_L":[(0,0,-.12)]*7,"thigh_R":[(0,0,.12)]*7};add("Punch",t,c,False)
 add("Shoot",[0,.5,1],{"upperarm_L":[(0,.98,0)]*3,"upperarm_R":[(0,-.98,0)]*3,"forearm_L":[(0,0,.62)]*3,"forearm_R":[(0,0,-.62)]*3,"spine":[(-.13,0,0)]*3,"chest":[(-.035,0,0)]*3,"thigh_L":[(.05,0,-.08)]*3,"thigh_R":[(-.05,0,.08)]*3})
 add("Emote",[0,.35,.7,1.05,1.4,1.8],{"upperarm_L":[(0,0,1.28)]*6,"forearm_L":[(0,0,.12)]*6,"upperarm_R":[(0,0,-.45),(0,0,-.40),(0,0,-.8),(0,0,-.4),(0,0,-.9),(0,0,-.45)],"forearm_R":[(0,0,-.15)]*6,"head":[(0,0,0),(0,.08,0),(0,0,0),(0,-.08,0),(0,0,0),(0,0,0)]})
 return out

def build(src:Path,dst:Path):
 original=src.read_bytes();d,b=parse_glb(original)
 if len(d.get("nodes",[]))!=1 or len(d.get("meshes",[]))!=1:raise ValueError("Expected inspected single-node/single-mesh source")
 prim=d["meshes"][0]["primitives"][0]
 if "JOINTS_0" in prim["attributes"] or d.get("skins") or d.get("animations"):raise ValueError("Refusing to overwrite an existing rig")
 pos=read_accessor(d,b,prim["attributes"]["POSITION"]).astype(np.float32);ji,we=skin_weights(pos)
 node=d["nodes"][0];scale=node.pop("scale",[1,1,1]);translation=node.pop("translation",None);rotation=node.pop("rotation",None)
 root=len(d["nodes"]);skroot=root+1;d["nodes"] += [{"name":"Character03_Root","scale":scale,"children":[0,skroot]},{"name":"Character03_SkeletonRoot","children":[]}]
 d.setdefault("scenes",[{"nodes":[0]}])[0]["nodes"]=[root]
 if translation is not None:node["translation"]=translation
 if rotation is not None:node["rotation"]=rotation
 ids={}
 for name,parent,p,sigma in BONES:
  ids[name]=len(d["nodes"]);pp=next(x[2] for x in BONES if x[0]==parent) if parent else (0,-.99,0);local=[p[i]-pp[i] for i in range(3)];d["nodes"].append({"name":name,"translation":local,"children":[]})
 for name,parent,p,sigma in BONES:d["nodes"][skroot if parent is None else ids[parent]].setdefault("children",[]).append(ids[name])
 jv=view(d,b,ji.astype("<u2").tobytes(),34962);wv=view(d,b,we.astype("<f4").tobytes(),34962)
 prim["attributes"]["JOINTS_0"]=accessor(d,jv,5123,len(pos),"VEC4");prim["attributes"]["WEIGHTS_0"]=accessor(d,wv,5126,len(pos),"VEC4")
 ibm=np.zeros((len(BONES),16),np.float32)
 for i,(name,parent,p,sigma) in enumerate(BONES):ibm[i]=[1,0,0,0,0,1,0,0,0,0,1,0,-p[0],-p[1],-p[2],1]
 iba=accessor(d,view(d,b,ibm.astype("<f4").tobytes()),5126,len(BONES),"MAT4")
 d.setdefault("skins",[]).append({"name":"Character03_HumanoidSkin","inverseBindMatrices":iba,"skeleton":skroot,"joints":[ids[x[0]] for x in BONES]});node["skin"]=0
 animations=[]
 for cname,times,curves,loop in clips():
  tv=accessor(d,view(d,b,np.asarray(times,dtype="<f4").tobytes()),5126,len(times),"SCALAR");samplers=[];channels=[]
  for bone,values in curves.items():
   if bone not in ids or len(values)!=len(times):raise ValueError("Invalid animation curve: "+bone)
   out=np.asarray([qxyz(v) for v in values],dtype="<f4");ov=accessor(d,view(d,b,out.tobytes()),5126,len(out),"VEC4");si=len(samplers);samplers.append({"input":tv,"output":ov,"interpolation":"LINEAR"});channels.append({"sampler":si,"target":{"node":ids[bone],"path":"rotation"}})
  animations.append({"name":cname,"samplers":samplers,"channels":channels,"extras":{"loop":loop,"duration":times[-1]}})
 d["animations"]=animations;d.setdefault("asset",{}).setdefault("extras",{})["wildboundCharacter03Rig"]={"generator":"scripts/rig_character03.py","version":1,"jointCount":len(BONES),"influencesPerVertex":4,"clips":[x[0] for x in clips()],"sourceMeshAndImageViewsPreserved":True}
 output=pack_glb(d,b);dst.write_bytes(output)
 return {"inputSha256":hashlib.sha256(original).hexdigest(),"outputSha256":hashlib.sha256(output).hexdigest(),"vertices":len(pos),"joints":len(BONES),"clips":[x[0] for x in clips()],"bytes":len(output)}

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("output",type=Path);a=p.parse_args();print(json.dumps(build(a.input,a.output),indent=2))
