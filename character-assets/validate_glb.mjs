#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import process from 'node:process';
import { NodeIO } from '@gltf-transform/core';

const fail = (message) => { console.error(`FAIL: ${message}`); process.exitCode = 1; };
const file = process.argv[2];
if (!file) {
  console.error('Usage: node character-assets/validate_glb.mjs <model.glb> [--require-rig] [--require-animation]');
  process.exit(2);
}
const absolute = path.resolve(file);
if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
  console.error(`Input file does not exist: ${absolute}`);
  process.exit(2);
}
const requireRig = process.argv.includes('--require-rig');
const requireAnimation = process.argv.includes('--require-animation');
try {
  const io = new NodeIO();
  const doc = await io.read(absolute);
  const root = doc.getRoot();
  const meshes = root.listMeshes();
  const skins = root.listSkins();
  const nodes = root.listNodes();
  const animations = root.listAnimations();
  const issues = [];
  if (meshes.length === 0) issues.push('no meshes found');
  if (requireRig && skins.length === 0) issues.push('no skins found');
  if (requireAnimation && animations.length === 0) issues.push('no animations found');
  for (const [index, skin] of skins.entries()) {
    const joints = skin.listJoints();
    if (joints.length === 0) issues.push(`skin ${index} has no joints`);
    const seen = new Set();
    for (const joint of joints) {
      if (!nodes.includes(joint)) issues.push(`skin ${index} references a node outside the document`);
      if (seen.has(joint)) issues.push(`skin ${index} contains a duplicate joint`);
      seen.add(joint);
    }
    const inverseBind = skin.getInverseBindMatrices();
    if (inverseBind) {
      const values = inverseBind.getArray();
      if (!values || Array.from(values).some((n) => !Number.isFinite(n))) issues.push(`skin ${index} has non-finite inverse bind matrices`);
      if (values && values.length !== joints.length * 16) issues.push(`skin ${index} inverse bind matrix count does not match joints`);
    }
  }
  let primitiveCount = 0;
  let jointAccessorCount = 0;
  let weightAccessorCount = 0;
  for (const [meshIndex, mesh] of meshes.entries()) {
    for (const [primitiveIndex, primitive] of mesh.listPrimitives().entries()) {
      primitiveCount++;
      const position = primitive.getAttribute('POSITION');
      if (!position) issues.push(`mesh ${meshIndex} primitive ${primitiveIndex} has no POSITION`);
      const joints = [primitive.getAttribute('JOINTS_0'), primitive.getAttribute('JOINTS_1')].filter(Boolean);
      const weights = [primitive.getAttribute('WEIGHTS_0'), primitive.getAttribute('WEIGHTS_1')].filter(Boolean);
      if (joints.length !== weights.length) issues.push(`mesh ${meshIndex} primitive ${primitiveIndex} has unmatched JOINTS/WEIGHTS attributes`);
      if (joints.length && !primitive.getMesh().getParentNode()?.getSkin()) issues.push(`mesh ${meshIndex} primitive ${primitiveIndex} has joint attributes but no node skin binding`);
      for (let set = 0; set < weights.length; set++) {
        const j = joints[set].getArray();
        const w = weights[set].getArray();
        if (!j || !w || j.length !== w.length) { issues.push(`mesh ${meshIndex} primitive ${primitiveIndex} has malformed joint/weight accessors`); continue; }
        jointAccessorCount++;
        weightAccessorCount++;
        for (let k = 0; k < w.length; k += 4) {
          const sum = w[k] + w[k + 1] + w[k + 2] + w[k + 3];
          if (![w[k],w[k+1],w[k+2],w[k+3],sum].every(Number.isFinite)) { issues.push(`mesh ${meshIndex} primitive ${primitiveIndex} has non-finite skin weights`); break; }
          if ([w[k],w[k+1],w[k+2],w[k+3]].some((v) => v < -1e-6)) { issues.push(`mesh ${meshIndex} primitive ${primitiveIndex} has negative skin weights`); break; }
          if (sum > 1e-5 && Math.abs(sum - 1) > 0.025) { issues.push(`mesh ${meshIndex} primitive ${primitiveIndex} has non-normalized skin weights (sum ${sum})`); break; }
        }
        const jointCount = primitive.getMesh().getParentNode()?.getSkin()?.listJoints().length ?? 0;
        for (const value of j) if (value >= jointCount) { issues.push(`mesh ${meshIndex} primitive ${primitiveIndex} has a joint index outside the bound skin`); break; }
      }
    }
  }
  const clipData = animations.map((animation) => {
    const channels = animation.listChannels();
    let duration = 0;
    for (const channel of channels) {
      const sampler = channel.getSampler();
      const input = sampler?.getInput();
      if (input) {
        const values = input.getArray();
        if (values?.length) duration = Math.max(duration, Number(values[values.length - 1]));
      }
    }
    if (channels.length === 0) issues.push(`animation ${animation.getName() || '(unnamed)'} has no channels`);
    return {name: animation.getName() || '(unnamed)', channels: channels.length, durationSeconds: Number(duration.toFixed(4))};
  });
  const stat = fs.statSync(absolute);
  const sha256 = crypto.createHash('sha256').update(fs.readFileSync(absolute)).digest('hex');
  const report = {
    file: path.basename(absolute), bytes: stat.size, sha256,
    meshes: meshes.length, primitives: primitiveCount, nodes: nodes.length,
    skins: skins.length, jointsPerSkin: skins.map((skin) => skin.listJoints().length),
    jointAccessors: jointAccessorCount, weightAccessors: weightAccessorCount,
    animations: clipData, issues
  };
  console.log(JSON.stringify(report, null, 2));
  if (issues.length) process.exitCode = 1;
} catch (error) {
  fail(error instanceof Error ? error.stack || error.message : String(error));
}
