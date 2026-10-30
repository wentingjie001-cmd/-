const assert = require("node:assert/strict");
const { test } = require("node:test");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const C = require("../js/curriculum.js");
const S = require("../js/session.js");
const { Engine } = require("../js/engine.js");

const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
};
const flush = () => new Promise((resolve) => setImmediate(resolve));

// Execute the real app and engine with controlled browser IO, no dependencies.
function app({ microphone, wakeRequest, unlock, autoSpeech = false } = {}) {
  const elements = new Map();
  const html = fs.readFileSync(path.join(__dirname, "../index.html"), "utf8");
  for (const [, id] of html.matchAll(/id="([^"]+)"/g)) {
    elements.set(id, {
      hidden: false, disabled: false, dataset: {}, style: {}, textContent: "",
      classList: { toggle() {} }, addEventListener() {},
      querySelector: () => ({ style: {}, getBoundingClientRect() {} }),
    });
  }
  let time = 0, saved = null, pending = null;
  const intervals = new Set();
  const engines = [];
  const requests = { mic: 0, wake: 0, releases: 0, trackStops: 0 };
  const stream = { getTracks: () => [{ stop: () => requests.trackStops++ }] };
  const lock = { release: async () => { requests.releases++; } };
  const wait = (ms) => {
    if (autoSpeech) {
      time += ms;
      return Promise.resolve({ aborted: false, transcript: "" });
    }
    assert.equal(pending, null, "only one speech operation may be pending");
    const d = deferred();
    pending = d;
    return d.promise;
  };
  const speech = {
    canListen: true, canSpeak: true, zh: {},
    loadVoices: async () => [], pickVoices() {}, englishVoices: () => [{}],
    unlock: unlock || (() => {}), cue() {},
    say: (text, lang, rate) => wait(S.estimateSayMs(text, lang, rate)),
    listen: wait, sleep: wait,
    cancel() {
      if (pending) {
        const d = pending;
        pending = null;
        d.resolve({ aborted: true, transcript: "" });
      }
    },
  };
  class ObservedEngine extends Engine {
    constructor(...args) { super(...args); engines.push(this); }
  }
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, "../js/app.js"), "utf8"), {
    window: { DEC: { curriculum: C, session: S, engine: { Engine: ObservedEngine }, speech }, scrollTo() {} },
    document: { getElementById: (id) => {
      assert.ok(elements.has(id), `known DOM id: ${id}`);
      return elements.get(id);
    }, addEventListener() {} },
    navigator: {
      mediaDevices: { getUserMedia: () => { requests.mic++; return microphone ? microphone() : Promise.resolve(stream); } },
      wakeLock: { request: () => { requests.wake++; return wakeRequest ? wakeRequest() : Promise.resolve(lock); } },
    },
    performance: { now: () => time },
    localStorage: { getItem: () => saved, setItem: (_, value) => { saved = value; } },
    setInterval: (fn) => { intervals.add(fn); return fn; },
    clearInterval: (fn) => intervals.delete(fn),
    confirm: () => true,
    console,
  }, { filename: "app.js" });
  return {
    elements, engines, requests, intervals, speech, stream, lock,
    click: (id) => elements.get(id).onclick(),
    setTime: (ms) => { time = ms; },
    progress: () => JSON.parse(saved).progress,
    pending: () => pending,
  };
}

test("repeated Start is ignored while microphone, wake lock, or session is pending; retry after hangup works", async () => {
  const mic = deferred(), wake = deferred();
  const a = app({ microphone: () => mic.promise, wakeRequest: () => wake.promise });
  const first = a.click("startBtn");
  assert.equal(a.elements.get("startBtn").disabled, true);
  await a.click("startBtn");
  assert.equal(a.requests.mic, 1);
  mic.resolve(a.stream);
  await flush();
  await a.click("startBtn");
  assert.equal(a.requests.trackStops, 1);
  assert.equal(a.requests.wake, 1);
  assert.equal(a.engines.length, 0);
  wake.resolve(a.lock);
  await flush();
  await a.click("startBtn");
  assert.equal(a.engines.length, 1);
  assert.equal(a.intervals.size, 1);
  a.click("btnHangup");
  await first;
  assert.equal(a.intervals.size, 0);
  assert.equal(a.requests.releases, 1);
  assert.equal(a.pending(), null);
  assert.equal(a.elements.get("startBtn").disabled, false);
  a.click("backHome");
  const second = a.click("startBtn");
  await flush();
  assert.equal(a.engines.length, 2);
  a.click("btnHangup");
  await second;
  assert.equal(a.progress().sessions.length, 2);
});

test("permission failures fall back to one fixed-tempo session", async () => {
  const a = app({
    microphone: async () => { throw new Error("permission denied"); },
    wakeRequest: async () => { throw new Error("wake lock unavailable"); },
  });
  const run = a.click("startBtn");
  await a.click("startBtn");
  await flush();
  assert.equal(a.engines.length, 1);
  assert.equal(a.speech.listenEnabled, false);
  assert.equal(a.elements.get("tglMic").checked, false);
  a.click("btnHangup");
  await run;
  assert.equal(a.elements.get("startBtn").disabled, false);
  assert.equal(a.requests.releases, 0);
});

test("unexpected startup failure releases the guard and allows retry", async () => {
  let fail = true;
  const a = app({ unlock: () => { if (fail) throw new Error("audio unavailable"); } });
  await a.click("startBtn");
  assert.equal(a.elements.get("startBtn").disabled, false);
  assert.equal(a.elements.get("home").hidden, false);
  assert.equal(a.elements.get("envWarn").hidden, false);
  assert.equal(a.intervals.size, 0);
  fail = false;
  const run = a.click("startBtn");
  await flush();
  assert.equal(a.engines.length, 1);
  a.click("btnHangup");
  await run;
});

test("session IO failure cleans up timer, speech and wake lock, then permits retry", async () => {
  const a = app();
  const first = a.click("startBtn");
  await flush();
  a.pending().reject(new Error("audio failed"));
  await first;
  assert.equal(a.intervals.size, 0);
  assert.equal(a.requests.releases, 1);
  assert.equal(a.pending(), null);
  assert.equal(a.speech.onState, null);
  assert.equal(a.elements.get("startBtn").disabled, false);
  const second = a.click("startBtn");
  await flush();
  a.click("btnHangup");
  await second;
  assert.equal(a.progress().sessions.length, 1, "failed run must not record a completion");
});

for (const elapsedMs of [0, 18 * 60000 - 1, 18 * 60000, 19 * 60000]) {
  test(`skipping all blocks at ${elapsedMs} ms credits completion only at 18 minutes`, async () => {
    const a = app();
    const run = a.click("startBtn");
    await flush();
    const e = a.engines[0];
    for (let i = 0; i < e.session.blocks.length; i++) {
      if (i === e.session.blocks.length - 1) a.setTime(elapsedMs);
      a.click("btnNextBlock");
      await flush();
    }
    await run;
    assert.equal(e.stats.completed, true, "reached engine end, even though blocks were skipped");
    const p = a.progress();
    const completed = elapsedMs >= 18 * 60000;
    assert.equal(p.sessions.length, 1);
    assert.equal(p.sessions[0].completed, completed);
    assert.equal(p.day, completed ? 2 : 1);
    assert.equal(p.streak, completed ? 1 : 0);
    assert.equal(Boolean(p.done[1]), completed);
    assert.equal(Boolean(p.lastDate), completed);
    assert.equal(a.elements.get("doneBadge").textContent, completed ? "✓" : "…");
    assert.equal(a.elements.get("done").hidden, false);
  });
}

test("paused time does not count towards the 18-minute completion threshold", async () => {
  const a = app();
  const run = a.click("startBtn");
  await flush();
  a.setTime(17 * 60000);
  a.click("btnPause");
  a.setTime(25 * 60000);
  a.click("btnHangup");
  await run;
  assert.equal(a.progress().sessions[0].completed, false);
  assert.equal(a.progress().sessions[0].minutes, 17);
  assert.equal(a.progress().day, 1);
});

test("skipping the final wrap-up turns cannot turn a short session into a completion", async () => {
  const a = app();
  const run = a.click("startBtn");
  await flush();
  const e = a.engines[0];
  for (let i = 0; i < e.session.blocks.length - 1; i++) {
    a.click("btnNextBlock");
    await flush();
  }
  // The finite wrap-up generator reaches engine.finish(true) after these skips.
  const wrapTurns = [...e.session.blocks.at(-1).turns()].length;
  for (let i = 0; i < wrapTurns; i++) {
    a.click("btnSkip");
    await flush();
  }
  await run;
  assert.equal(e.stats.completed, true);
  assert.equal(a.progress().sessions[0].completed, false);
  assert.equal(a.progress().day, 1);
});

test("hanging up at 18 minutes still earns completion credit", async () => {
  const a = app();
  const run = a.click("startBtn");
  await flush();
  a.setTime(18 * 60000);
  a.click("btnHangup");
  await run;
  assert.equal(a.engines[0].stats.completed, false, "engine was stopped early");
  assert.equal(a.progress().sessions[0].completed, true);
  assert.equal(a.progress().day, 2);
  assert.equal(a.progress().streak, 1);
});

test("a full 20-minute session records completion and allows a new session", async () => {
  const a = app({ autoSpeech: true });
  await a.click("startBtn");
  const p = a.progress();
  assert.ok(p.sessions[0].minutes >= 19.5 && p.sessions[0].minutes <= 21);
  assert.equal(p.sessions[0].completed, true);
  assert.equal(p.day, 2);
  assert.equal(p.streak, 1);
  assert.equal(a.elements.get("startBtn").disabled, false);
  assert.equal(a.intervals.size, 0);
  assert.equal(a.requests.releases, 1);
  a.click("backHome");
  await a.click("startBtn");
  assert.equal(a.progress().day, 3);
  assert.equal(a.progress().sessions.length, 2);
  assert.equal(a.progress().streak, 1, "two sessions on one day only count one streak day");
  assert.equal(a.requests.releases, 2);
});
