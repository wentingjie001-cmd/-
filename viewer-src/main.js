import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';

const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
const ease = (t) => t * t * (3 - 2 * t);

// Model coordinates: mm, X across, Y from the wearer's back towards the pack, Z up.
// The wearer faces -Y, so the wearer's right-hand side is -X.
const VIEWS = [
  { key: 'rear34', name: '斜后', dir: [1.0, -1.3, 0.45] },
  { key: 'front34', name: '斜前', dir: [0.95, 1.45, 0.5] },
  { key: 'rear', name: '背负面', dir: [0, -1, 0.06] },
  { key: 'front', name: '正面', dir: [0, 1, 0.06] },
  { key: 'side', name: '侧面', dir: [1, 0, 0.05] },
  { key: 'top', name: '俯视', dir: [0, -0.04, 1] },
];
const TOURS = [
  { key: 'whole', name: '整包', dir: [0.95, 1.45, 0.5] },
  { key: 'worn', name: '背负面', dir: [1.0, -1.3, 0.45] },
  { key: 'system', name: '背负系统', dir: [0.62, -1.5, 0.35], off: ['shoulder', 'belt'] },
  { key: 'linkage', name: '联动机构', dir: [0.85, -1.25, 0.2], off: ['pad'], xray: true, focus: ['hub', 'linkage', 'shoulder'] },
  { key: 'exploded', name: '拆解图', dir: [0.9, -0.85, 0.22], explode: 1, exploded: true },
];
const HUB_VIEW = { dir: [0.75, 1.2, 0.35], only: ['hub', 'linkage', 'shoulder'], focus: ['hub', 'linkage'] };

function fail(msg) {
  const el = $('#loading');
  el.hidden = false;
  el.textContent = msg;
}

function decode(b64) {
  const s = atob(b64);
  const out = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i++) out[i] = s.charCodeAt(i);
  return out.buffer;
}

function start() {
  const model = window.BP40_MODEL;
  if (!model) return fail('没有找到模型数据 model.js。');
  const M = model.manifest;
  const buf = decode(model.data);
  model.data = null;

  const canvas = $('#view');
  const stage = $('#stage');
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  } catch (e) {
    return fail('这个浏览器打不开 3D 画面（WebGL 不可用）。请换用系统浏览器或 Chrome 再试。');
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0x000000, 0);

  THREE.Object3D.DEFAULT_UP.set(0, 0, 1);
  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.55;
  pmrem.dispose();

  const camera = new THREE.PerspectiveCamera(24, 1, 20, 20000);
  camera.up.set(0, 0, 1);
  scene.add(camera);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x9aa3ad, 0.9));
  const key = new THREE.DirectionalLight(0xffffff, 2.1);
  key.position.set(-0.6, 0.9, 1.0); // camera space: up and to the left of the viewer
  camera.add(key);
  camera.add(key.target);
  key.target.position.set(0, 0, -1);
  const fill = new THREE.DirectionalLight(0xffffff, 0.55);
  fill.position.set(1.0, -0.2, 0.6);
  camera.add(fill);

  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.09;
  controls.rotateSpeed = 0.9;
  controls.zoomSpeed = 1.1;
  controls.minDistance = 220;
  controls.maxDistance = 9000;
  controls.autoRotateSpeed = 1.6;

  // ---------------------------------------------------------------- parts
  const span = [0, 1, 2].map((c) => (M.hi[c] - M.lo[c]) / 65535);
  const floats = (off, nv) => {
    const q = new Uint16Array(buf, off, nv * 3);
    const out = new Float32Array(nv * 3);
    for (let i = 0; i < out.length; i++) out[i] = M.lo[i % 3] + q[i] * span[i % 3];
    return out;
  };

  const root = new THREE.Group();
  scene.add(root);
  const layers = new Map();
  for (const l of M.layers) {
    const group = new THREE.Group();
    root.add(group);
    layers.set(l.key, { ...l, group, on: true, parts: [] });
  }
  const parts = [];
  const posed = [];
  for (const d of M.parts) {
    const rest = floats(d.pos, d.nv);
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(rest.slice(), 3));
    const idx = d.wide ? new Uint32Array(buf, d.idx, d.nt * 3) : new Uint16Array(buf, d.idx, d.nt * 3);
    geo.setIndex(new THREE.BufferAttribute(idx, 1));
    geo.computeVertexNormals();
    geo.computeBoundingBox();
    geo.computeBoundingSphere();
    const mat = new THREE.MeshStandardMaterial({
      color: new THREE.Color().setRGB(d.color[0], d.color[1], d.color[2], THREE.SRGBColorSpace),
      roughness: d.shiny ? 0.38 : 0.86,
      metalness: d.shiny ? 0.75 : 0.0,
      side: THREE.DoubleSide,
    });
    const mesh = new THREE.Mesh(geo, mat);
    const part = { ...d, mesh, mat, geo, rest, hidden: false, delta: null };
    mesh.userData.part = part;
    if (Object.keys(d.poses).length) {
      part.delta = {};
      for (const [name, off] of Object.entries(d.poses)) {
        const p = floats(off, d.nv);
        for (let i = 0; i < p.length; i++) p[i] -= rest[i];
        part.delta[name] = p;
      }
      geo.attributes.position.setUsage(THREE.DynamicDrawUsage);
      posed.push(part);
    }
    const layer = layers.get(d.layer);
    layer.group.add(mesh);
    layer.parts.push(part);
    parts.push(part);
  }
  const lever = parts.find((p) => p.key === 'cam_lever');
  if (lever) lever.mesh.matrixAutoUpdate = false;

  // soft contact shadow under the pack
  const shadowTex = (() => {
    const c = document.createElement('canvas');
    c.width = c.height = 128;
    const g = c.getContext('2d');
    const grad = g.createRadialGradient(64, 64, 4, 64, 64, 64);
    grad.addColorStop(0, 'rgba(20,30,40,0.55)');
    grad.addColorStop(0.55, 'rgba(20,30,40,0.18)');
    grad.addColorStop(1, 'rgba(20,30,40,0)');
    g.fillStyle = grad;
    g.fillRect(0, 0, 128, 128);
    return new THREE.CanvasTexture(c);
  })();
  const shadow = new THREE.Mesh(
    new THREE.PlaneGeometry(760, 900),
    new THREE.MeshBasicMaterial({ map: shadowTex, transparent: true, depthWrite: false, opacity: 0.8 }),
  );
  shadow.position.set(0, 40, M.lo[2] - 2);
  shadow.renderOrder = -1;
  root.add(shadow);

  // ---------------------------------------------------------------- state
  const state = {
    sway: 0, // mm of web run towards the wearer's right-hand strap
    torso: 0,
    torsoTo: 0,
    rung: (M.torsoRungs - 1) / 2,
    explode: 0,
    explodeTo: 0,
    locked: false,
    lever: 0,
    walking: false,
    walkT: 0,
    xray: false,
    selected: null,
  };
  let dirty = true;
  let camAnim = null;
  const invalidate = () => { dirty = true; };
  controls.addEventListener('change', invalidate);

  function applyPose() {
    const ws = clamp(Math.abs(state.sway) / M.swayMax, 0, 1);
    const tMax = M.torsoStep * (M.torsoRungs - 1) / 2;
    const wt = clamp(Math.abs(state.torso) / tMax, 0, 1);
    // +X is the wearer's left, so a positive (right-hand) sway is the model's negative pose
    const sName = state.sway > 0 ? 'sway_neg' : 'sway_pos';
    const tName = state.torso > 0 ? 'torso_pos' : 'torso_neg';
    for (const p of posed) {
      const a = p.geo.attributes.position.array;
      a.set(p.rest);
      const ds = ws > 0 ? p.delta[sName] : null;
      const dt = wt > 0 ? p.delta[tName] : null;
      if (ds) for (let i = 0; i < a.length; i++) a[i] += ws * ds[i];
      if (dt) for (let i = 0; i < a.length; i++) a[i] += wt * dt[i];
      p.geo.attributes.position.needsUpdate = true;
      p.geo.computeVertexNormals();
      p.geo.computeBoundingBox();
      p.geo.computeBoundingSphere();
    }
    invalidate();
  }

  function applyLever() {
    if (!lever) return;
    const [, py, pz] = M.leverPivot;
    const [sx, sy, sz] = M.leverShow;
    // the stored lever hangs inside the bag; swing it up onto the wearer side, then fold it down to lock
    const show = new THREE.Matrix4().makeTranslation(sx, sy, sz);
    show.multiply(new THREE.Matrix4().makeRotationX(Math.PI / 2));
    show.multiply(new THREE.Matrix4().makeTranslation(0, -py, -pz));
    const fold = new THREE.Matrix4().makeTranslation(sx, sy, sz);
    fold.multiply(new THREE.Matrix4().makeRotationX(state.lever * 1.15));
    fold.multiply(new THREE.Matrix4().makeTranslation(-sx, -sy, -sz));
    lever.mesh.matrix.copy(fold.multiply(show));
    lever.mesh.matrixWorldNeedsUpdate = true;
    invalidate();
  }

  function applyExplode() {
    for (const l of layers.values()) l.group.position.y = state.explode * l.explode;
    shadow.material.opacity = 0.8 * (1 - state.explode);
    shadow.visible = state.explode < 0.98;
    invalidate();
  }

  function applyVisibility() {
    for (const l of layers.values()) {
      l.group.visible = l.on;
      for (const p of l.parts) p.mesh.visible = !p.hidden;
    }
    const bag = layers.get('bag');
    for (const p of bag.parts) {
      p.mat.transparent = state.xray;
      p.mat.opacity = state.xray ? 0.16 : 1;
      p.mat.depthWrite = !state.xray;
      p.mesh.renderOrder = state.xray ? 5 : 0;
      p.mat.needsUpdate = true;
    }
    for (const b of $$('#layers .chip')) b.setAttribute('aria-pressed', String(layers.get(b.dataset.layer).on));
    $('#xray').setAttribute('aria-pressed', String(state.xray));
    invalidate();
  }

  // ---------------------------------------------------------------- camera
  function visibleBox(only) {
    const box = new THREE.Box3();
    const tmp = new THREE.Box3();
    for (const l of layers.values()) {
      if (!l.on || (only && !only.includes(l.key))) continue;
      for (const p of l.parts) {
        if (p.hidden) continue;
        tmp.copy(p.geo.boundingBox).translate(new THREE.Vector3(0, state.explodeTo * l.explode, 0));
        box.union(tmp);
      }
    }
    if (box.isEmpty()) box.set(new THREE.Vector3(...M.lo), new THREE.Vector3(...M.hi));
    return box;
  }

  function modelBox() {
    const box = new THREE.Box3();
    const tmp = new THREE.Box3();
    for (const l of layers.values()) {
      if (!l.on) continue;
      for (const p of l.parts) {
        if (p.hidden) continue;
        tmp.copy(p.geo.boundingBox);
        box.union(tmp);
      }
    }
    if (box.isEmpty()) box.set(new THREE.Vector3(...M.lo), new THREE.Vector3(...M.hi));
    return box;
  }

  function fit(dir, only, exploded) {
    const box = only ? visibleBox(only) : exploded ? modelBox() : visibleBox(null);
    const target = box.getCenter(new THREE.Vector3());
    const d = new THREE.Vector3(...dir).normalize();
    const right = new THREE.Vector3().crossVectors(new THREE.Vector3(0, 0, 1), d).normalize();
    const up = new THREE.Vector3().crossVectors(d, right).normalize();
    let mx = 0, my = 0, mz = 0;
    for (let i = 0; i < 8; i++) {
      const c = new THREE.Vector3(i & 1 ? box.max.x : box.min.x, i & 2 ? box.max.y : box.min.y, i & 4 ? box.max.z : box.min.z).sub(target);
      mx = Math.max(mx, Math.abs(c.dot(right)));
      my = Math.max(my, Math.abs(c.dot(up)));
      mz = Math.max(mz, c.dot(d));
    }
    const th = Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2);
    const dist = Math.max(my / th, mx / (th * camera.aspect)) * 1.1 + mz;
    return { target, pos: target.clone().addScaledVector(d, dist) };
  }

  function flyTo(dir, only, ms = 650, exploded = false) {
    const to = fit(dir, only, exploded);
    if (!ms) {
      camera.position.copy(to.pos);
      controls.target.copy(to.target);
      controls.update();
      invalidate();
      return;
    }
    const o0 = camera.position.clone().sub(controls.target);
    const o1 = to.pos.clone().sub(to.target);
    camAnim = {
      t: 0, ms,
      t0: controls.target.clone(), t1: to.target,
      d0: o0.clone().normalize(), d1: o1.clone().normalize(),
      l0: o0.length(), l1: o1.length(),
    };
  }

  function currentDir() {
    return camera.position.clone().sub(controls.target).normalize().toArray();
  }

  // ---------------------------------------------------------------- UI
  const tabs = $$('.tabs button');
  const panes = $$('.pane');
  function showTab(name) {
    for (const b of tabs) b.setAttribute('aria-selected', String(b.dataset.tab === name));
    for (const p of panes) p.hidden = p.dataset.pane !== name;
  }
  for (const b of tabs) b.addEventListener('click', () => showTab(b.dataset.tab));

  const mkBtn = (cls, text, parent, fn) => {
    const b = document.createElement('button');
    b.className = cls;
    b.textContent = text;
    b.addEventListener('click', () => fn(b));
    parent.appendChild(b);
    return b;
  };

  for (const v of VIEWS) mkBtn('btn', v.name, $('#views'), () => flyTo(v.dir));

  function setLayers(off = [], only = null) {
    for (const l of layers.values()) l.on = only ? only.includes(l.key) : !off.includes(l.key);
    for (const p of parts) p.hidden = false;
  }
  function setExplode(v, refit = true) {
    state.explodeTo = clamp(v, 0, 1);
    $('#explode').value = Math.round(state.explodeTo * 100);
    if (refit) flyTo(currentDir(), null, 650, state.explodeTo > 0.05);
  }
  for (const t of TOURS) {
    mkBtn('btn', t.name, $('#tours'), () => {
      setLayers(t.off || []);
      state.xray = !!t.xray;
      applyVisibility();
      setExplode(t.explode || 0, false);
      select(null);
      flyTo(t.dir, t.focus, 650, !!t.exploded);
    });
  }

  for (const l of layers.values()) {
    const b = mkBtn('chip', l.name, $('#layers'), () => {
      l.on = !l.on;
      if (state.selected && state.selected.layer === l.key && !l.on) select(null);
      applyVisibility();
    });
    b.dataset.layer = l.key;
  }
  $('#xray').addEventListener('click', () => { state.xray = !state.xray; applyVisibility(); });
  $('#show-all').addEventListener('click', () => { setLayers(); state.xray = false; applyVisibility(); });

  $('#explode').addEventListener('input', (e) => { state.explodeTo = e.target.value / 100; state.explode = state.explodeTo; applyExplode(); });
  $('#explode').addEventListener('change', () => flyTo(currentDir()));
  for (const b of $$('[data-explode]')) b.addEventListener('click', () => setExplode(b.dataset.explode / 100));

  const swayInput = $('#sway');
  swayInput.min = -M.swayMax;
  swayInput.max = M.swayMax;
  $('#sway-max').textContent = `±${M.swayMax} mm`;
  $('#torso-step').textContent = `${M.torsoStep} mm`;

  function swayReadout() {
    const v = Math.round(state.sway);
    const el = $('#sway-read');
    const lockNote = state.locked ? '已锁止：凸轮压住联动带，两侧肩带不再走带。' : '';
    if (v === 0) el.innerHTML = `${lockNote}联动带居中，两侧肩带一样长。`;
    else {
      const [long, short] = v > 0 ? ['右', '左'] : ['左', '右'];
      const end = Math.abs(v) >= M.swayMax ? '（到限位）' : '';
      el.innerHTML = `${lockNote}${long}肩带下端放长 <em>${Math.abs(v)} mm</em>，${short}肩带收短 <em>${Math.abs(v)} mm</em>${end}`;
    }
    swayInput.value = v;
  }
  function setSway(v) {
    state.sway = clamp(v, -M.swayMax, M.swayMax);
    applyPose();
    swayReadout();
  }
  swayInput.addEventListener('input', (e) => { if (!state.locked) { setWalking(false); setSway(+e.target.value); } });

  function setWalking(on) {
    state.walking = on && !state.locked;
    if (state.walking) state.walkT = Math.asin(clamp(state.sway / (M.swayMax * 0.86), -1, 1));
    const b = $('#walk');
    b.setAttribute('aria-pressed', String(state.walking));
    b.textContent = state.walking ? '停止摆动' : '演示走路摆动';
    b.classList.toggle('primary', !state.walking);
  }
  $('#walk').addEventListener('click', () => setWalking(!state.walking));

  function setLocked(on) {
    state.locked = on;
    if (on) setWalking(false);
    const b = $('#lock');
    b.setAttribute('aria-pressed', String(on));
    b.textContent = on ? '已锁止（点一下解锁）' : '锁止';
    swayInput.disabled = on;
    $('#walk').disabled = on;
    swayReadout();
  }
  $('#lock').addEventListener('click', () => setLocked(!state.locked));
  $('#see-hub').addEventListener('click', () => {
    setLayers([], HUB_VIEW.only);
    state.xray = false;
    applyVisibility();
    setExplode(0, false);
    select(null);
    flyTo(HUB_VIEW.dir, HUB_VIEW.focus);
  });

  const rungBtns = [];
  const mid = (M.torsoRungs - 1) / 2;
  function setRung(i) {
    state.rung = i;
    state.torsoTo = (i - mid) * M.torsoStep;
    rungBtns.forEach((b, k) => b.classList.toggle('sel', k === i));
    const dz = state.torsoTo;
    $('#torso-read').innerHTML = dz === 0
      ? `第 <em>${i + 1}</em> 档（中间档）`
      : `第 <em>${i + 1}</em> 档：肩轭比中间档${dz > 0 ? '高' : '低'} <em>${Math.abs(dz)} mm</em>`;
  }
  for (let i = 0; i < M.torsoRungs; i++) rungBtns.push(mkBtn('btn', `${i + 1} 档`, $('#rungs'), () => setRung(i)));

  $('#spin').addEventListener('click', (e) => {
    controls.autoRotate = !controls.autoRotate;
    e.currentTarget.setAttribute('aria-pressed', String(controls.autoRotate));
  });
  $('#reset').addEventListener('click', () => {
    setLayers();
    state.xray = false;
    applyVisibility();
    setWalking(false);
    setLocked(false);
    setSway(0);
    setRung(mid);
    setExplode(0, false);
    select(null);
    controls.autoRotate = false;
    $('#spin').setAttribute('aria-pressed', 'false');
    flyTo(VIEWS[0].dir);
  });

  $('#help-open').addEventListener('click', () => { $('#help').hidden = false; });
  $('#help-close').addEventListener('click', () => { $('#help').hidden = true; });
  $('#help').addEventListener('click', (e) => { if (e.target.id === 'help') e.target.hidden = true; });

  // ---------------------------------------------------------------- picking
  const info = $('#info');
  const hint = $('#hint');
  function select(part) {
    if (state.selected) state.selected.mat.emissive.setRGB(0, 0, 0);
    state.selected = part;
    if (part) {
      part.mat.emissive.setRGB(0.16, 0.3, 0.62);
      $('.name', info).textContent = part.name;
      $('.layer', info).textContent = `图层：${layers.get(part.layer).name}`;
      $('.dot', info).style.background = `#${part.mat.color.getHexString()}`;
      hint.hidden = true;
    }
    info.hidden = !part;
    invalidate();
  }
  $('#info-close').addEventListener('click', () => select(null));
  $('#info-hide').addEventListener('click', () => {
    if (!state.selected) return;
    state.selected.hidden = true;
    select(null);
    applyVisibility();
  });

  const ray = new THREE.Raycaster();
  function pick(x, y) {
    const r = canvas.getBoundingClientRect();
    ray.setFromCamera(new THREE.Vector2(((x - r.left) / r.width) * 2 - 1, -((y - r.top) / r.height) * 2 + 1), camera);
    const meshes = [];
    for (const l of layers.values()) {
      if (!l.on || (state.xray && l.key === 'bag')) continue;
      for (const p of l.parts) if (!p.hidden) meshes.push(p.mesh);
    }
    const hit = ray.intersectObjects(meshes, false)[0];
    select(hit ? hit.object.userData.part : null);
  }
  let down = null;
  const active = new Set();
  canvas.addEventListener('pointerdown', (e) => {
    active.add(e.pointerId);
    down = active.size === 1 ? { x: e.clientX, y: e.clientY, t: performance.now() } : null;
    camAnim = null;
    hint.style.opacity = '0';
  });
  const release = (e) => {
    active.delete(e.pointerId);
    if (e.type === 'pointerup' && down && Math.hypot(e.clientX - down.x, e.clientY - down.y) < 7 && performance.now() - down.t < 450) pick(e.clientX, e.clientY);
    down = null;
  };
  canvas.addEventListener('pointerup', release);
  canvas.addEventListener('pointercancel', release);
  canvas.addEventListener('contextmenu', (e) => e.preventDefault());

  // ---------------------------------------------------------------- loop
  function resize() {
    const w = stage.clientWidth, h = stage.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    invalidate();
  }
  new ResizeObserver(resize).observe(stage);
  resize();

  let last = performance.now();
  function frame(now) {
    requestAnimationFrame(frame);
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;

    if (camAnim) {
      camAnim.t = Math.min(1, camAnim.t + (dt * 1000) / camAnim.ms);
      const k = ease(camAnim.t);
      const q = new THREE.Quaternion().setFromUnitVectors(camAnim.d0, camAnim.d1);
      const d = camAnim.d0.clone().applyQuaternion(new THREE.Quaternion().slerp(q, k));
      controls.target.lerpVectors(camAnim.t0, camAnim.t1, k);
      camera.position.copy(controls.target).addScaledVector(d, camAnim.l0 + (camAnim.l1 - camAnim.l0) * k);
      if (camAnim.t >= 1) camAnim = null;
      dirty = true;
    }
    if (state.walking) {
      state.walkT += dt * ((2 * Math.PI) / 1.7);
      state.sway = M.swayMax * 0.86 * Math.sin(state.walkT);
      applyPose();
      swayReadout();
    }
    if (state.torso !== state.torsoTo) {
      const step = dt * 160;
      state.torso = Math.abs(state.torsoTo - state.torso) <= step ? state.torsoTo : state.torso + Math.sign(state.torsoTo - state.torso) * step;
      applyPose();
    }
    if (state.explode !== state.explodeTo) {
      const step = dt * 2.2;
      state.explode = Math.abs(state.explodeTo - state.explode) <= step ? state.explodeTo : state.explode + Math.sign(state.explodeTo - state.explode) * step;
      applyExplode();
    }
    const leverTo = state.locked ? 1 : 0;
    if (state.lever !== leverTo) {
      const step = dt * 4;
      state.lever = Math.abs(leverTo - state.lever) <= step ? leverTo : state.lever + Math.sign(leverTo - state.lever) * step;
      applyLever();
    }
    if (controls.update()) dirty = true;
    if (dirty) {
      dirty = false;
      renderer.render(scene, camera);
    }
  }

  showTab('view');
  setRung(mid);
  swayReadout();
  applyLever();
  applyExplode();
  applyVisibility();
  flyTo(VIEWS[0].dir, null, 0);
  $('#loading').hidden = true;
  requestAnimationFrame(frame);

  // small hook for automated checks
  window.BP40_VIEWER = { state, layers, parts, flyTo, setSway, setRung, setLocked, setExplode, select };
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
else start();
