/* BattleZone V6 command-deck live status. Existing game handlers remain authoritative. */
(() => {
  'use strict';
  const byId = (id) => document.getElementById(id);
  const title = byId('bz-v6-hero-title');
  const meta = byId('bz-v6-hero-meta');
  const lobby = byId('lobby');
  if (!title || !meta || !lobby) return;

  const clean = (value, fallback) => {
    const text = String(value || '').replace(/\s+/g, ' ').trim();
    return text || fallback;
  };

  const makeKeyboardOperable = () => {
    lobby.querySelectorAll('#maps .mc,#lb-l .card,#lb-nav b').forEach((node) => {
      if (!node.hasAttribute('tabindex')) node.tabIndex = 0;
      if (!node.hasAttribute('role')) node.setAttribute('role', 'button');
    });
  };

  const sync = () => {
    const mode = clean(byId('matchmode')?.textContent?.replace(/^Match:\s*/i, ''), 'Battle Royale');
    const team = clean(byId('sqd')?.textContent?.replace(/^Team:\s*/i, ''), 'Squad');
    const difficulty = clean(byId('dif')?.textContent?.replace(/^Bots:\s*/i, ''), 'Normal');
    const selected = lobby.querySelector('#maps .mc.on b');
    const map = clean(selected?.textContent, 'Selected battlefield');
    title.textContent = 'READY FOR DEPLOYMENT';
    meta.textContent = `${map.toUpperCase()} · ${mode.toUpperCase()} · ${team.toUpperCase()} · ${difficulty.toUpperCase()} AI`;
    const deploy = byId('go2');
    if (deploy && deploy.textContent.trim() !== 'DEPLOY') deploy.textContent = 'DEPLOY';
    makeKeyboardOperable();
  };

  ['sqd', 'matchmode', 'dif'].forEach((id) => {
    const node = byId(id);
    if (node) new MutationObserver(sync).observe(node, { childList: true, characterData: true, subtree: true });
  });
  const mapList = byId('maps');
  if (mapList) new MutationObserver(sync).observe(mapList, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
  lobby.addEventListener('keydown', (event) => {
    const control = event.target.closest('#maps .mc,#lb-l .card,#lb-nav b');
    if (control && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault();
      control.click();
    }
  });
  lobby.addEventListener('click', (event) => {
    if (event.target.closest('#sqd,#matchmode,#dif,#maps .mc')) requestAnimationFrame(sync);
  }, { passive: true });
  window.addEventListener('hashchange', sync, { passive: true });
  sync();
})();
