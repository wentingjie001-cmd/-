#!/usr/bin/env node
/*
 * Validates the curriculum and simulates sessions with a fake clock.
 *
 *   node tools/simulate.js            check days 1-40, print a summary table
 *   node tools/simulate.js --day 1    print the full timeline of one day
 *   node tools/simulate.js --asr      also simulate a learner speaking (exercises feedback paths)
 */
const C = require("../js/curriculum.js");
const S = require("../js/session.js");
const { Engine } = require("../js/engine.js");

const args = process.argv.slice(2);
const dayArg = args.includes("--day") ? parseInt(args[args.indexOf("--day") + 1], 10) : null;
const withAsr = args.includes("--asr");

let failures = 0;
const fail = (msg) => {
  failures++;
  console.error("FAIL:", msg);
};

// ───────────── curriculum checks ─────────────
const KEYS = ["title", "zh", "focus", "sounds", "pairs", "words", "phrases", "sentences", "talk"];
C.DAYS.forEach((d, i) => {
  const n = i + 1;
  for (const k of KEYS) if (d[k] === undefined) fail(`day ${n} missing ${k}`);
  if (!d.sounds.length) fail(`day ${n} has no sounds`);
  d.sounds.forEach((s) => {
    if (!s.label || !s.tip || !s.ex || !s.ex.length) fail(`day ${n} sound malformed: ${JSON.stringify(s)}`);
    s.ex.forEach((e) => e.length !== 2 && fail(`day ${n} sound example malformed: ${e}`));
  });
  d.pairs.forEach((p) => p.length !== 4 && fail(`day ${n} pair malformed: ${p}`));
  d.words.forEach((w) => (w.length !== 3 || !w[1]) && fail(`day ${n} word malformed: ${w}`));
  d.phrases.forEach((w) => (w.length !== 3 || !w[1]) && fail(`day ${n} phrase malformed: ${w}`));
  d.sentences.forEach((w) => w.length !== 2 && fail(`day ${n} sentence malformed: ${w}`));
  d.talk.forEach((w) => w.length !== 3 && fail(`day ${n} talk malformed: ${w}`));
  if (d.words.length < 6) fail(`day ${n} needs >= 6 words`);
  if (d.phrases.length < 5) fail(`day ${n} needs >= 5 phrases`);
  if (d.sentences.length < 4) fail(`day ${n} needs >= 4 sentences`);
  if (d.talk.length < 3) fail(`day ${n} needs >= 3 talk prompts`);
});
for (const [ph, b] of Object.entries(S.BUDGETS)) {
  const sum = Object.values(b).reduce((a, x) => a + x, 0);
  if (sum !== S.SESSION_SECONDS) fail(`phase ${ph} budget sums to ${sum}s, expected ${S.SESSION_SECONDS}s`);
}

// ───────────── unit checks ─────────────
const eq = (a, b, msg) => JSON.stringify(a) !== JSON.stringify(b) && fail(`${msg}: got ${JSON.stringify(a)}, want ${JSON.stringify(b)}`);
eq(S.backChain("Nice to meet you."), ["meet you.", "to meet you.", "Nice to meet you."], "backChain");
eq(S.backChain("Thank you."), ["Thank you."], "backChain short");
eq(S.speakable("I *can't* swim / ok (n.)"), "I can't swim, ok", "speakable");
eq(S.scoreSpeech("I'm fine, thank you.", "i am fine thank you"), 1, "score contractions");
eq(S.scoreSpeech("It's nine o'clock.", "it's 9:00"), 1, "score numbers");
eq(S.scoreSpeech("How are you?", ""), 0, "score empty");
if (S.scoreSpeech("Nice to meet you.", "nice meet") !== 0.5) fail("score partial");

// ───────────── simulation ─────────────
function simulate(dayNum, { log = false, asr = false } = {}) {
  let t = 0;
  let k = 0;
  const lines = [];
  const at = () => {
    const s = Math.floor(t / 1000);
    return `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
  };
  let current = null;
  const io = {
    now: () => t,
    say: async (text, lang, rate) => {
      if (log) lines.push(`${at()}  coach ${lang === "zh" ? "中" : "EN"}: ${text}`);
      t += S.estimateSayMs(text, lang, rate || 0.9);
      return { aborted: false };
    },
    listen: async (ms, o) => {
      if (log) lines.push(`${at()}      you (${o.kind}, ${(ms / 1000).toFixed(1)}s)${o.expect ? ": " + o.expect : ""}`);
      t += ms;
      if (!asr) return { aborted: false, transcript: "" };
      k++;
      // Learner gets ~2/3 right, mumbles the rest.
      const transcript = o.expect ? (k % 3 ? o.expect : "um") : o.kind === "free" ? "my name is alex" : "two";
      return { aborted: false, transcript };
    },
    sleep: async (ms) => {
      t += ms;
      return { aborted: false };
    },
    cancel: () => {},
    show: (sh) => {
      current = sh;
    },
    onBlock: (i, b, w) => {
      if (log) lines.push(`\n── ${at()}  [${b.zh} · ${b.title}]  budget ${b.seconds}s, ends by ${(w.end / 1000).toFixed(0)}s ──`);
    },
  };
  const session = S.buildSession(dayNum, { name: "Alex", city: "Shanghai" }, { date: new Date(2026, 9, 30) });
  const engine = new Engine(session, io);
  return engine.run().then((stats) => ({ session, stats, lines, current }));
}

(async () => {
  if (dayArg) {
    const { session, stats, lines } = await simulate(dayArg, { log: true, asr: withAsr });
    console.log(`Day ${dayArg}: ${session.day.title} — ${session.day.zh}  (${session.phase.zh})`);
    console.log(lines.join("\n"));
    console.log(`\nTotal ${(stats.elapsedMs / 60000).toFixed(2)} min, ${stats.turns} turns`);
    console.log("Block durations:", stats.blocks.map((b) => `${b.key} ${(b.ms / 1000).toFixed(0)}s`).join(", "));
  } else {
    console.log("day  phase  minutes  turns  title");
    for (let d = 1; d <= 40; d++) {
      const { session, stats } = await simulate(d, { asr: withAsr });
      const min = stats.elapsedMs / 60000;
      if (!stats.completed) fail(`day ${d} did not complete`);
      if (min < 19.5 || min > 21) fail(`day ${d} ran ${min.toFixed(2)} min (want 19.5–21)`);
      for (const b of stats.blocks) {
        const budget = session.blocks.find((x) => x.key === b.key).seconds * 1000;
        if (b.key !== "wrap" && b.ms < budget * 0.5) fail(`day ${d} block ${b.key} only ran ${(b.ms / 1000).toFixed(0)}s of ${budget / 1000}s`);
      }
      console.log(`${String(d).padStart(3)}  ${session.phase.id}      ${min.toFixed(2)}    ${String(stats.turns).padStart(3)}    ${session.day.title}`);
    }
  }
  if (failures) {
    console.error(`\n${failures} check(s) failed`);
    process.exit(1);
  }
  console.log("\nAll checks passed.");
})();
