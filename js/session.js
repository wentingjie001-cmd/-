/*
 * Builds a 20-minute session for a given day.
 *
 * A session is a list of blocks. Each block has a time budget and a generator
 * that yields "turns" forever (cycling through rounds of increasing difficulty);
 * the engine stops pulling turns when the block's budget is used up.
 *
 * A turn = { show, ops } where ops are executed in order:
 *   { t: "say",  text, lang: "en" | "zh", rate }
 *   { t: "wait", ms, kind: "repeat" | "recall" | "read" | "free" | "quiz", expect?, correct? }
 *   { t: "show", show }
 *   { t: "gap",  ms }
 */
(function (root) {
  const C =
    typeof module !== "undefined" && module.exports && typeof require === "function"
      ? require("./curriculum.js")
      : root.DEC.curriculum;

  const SESSION_SECONDS = 20 * 60;

  // Block budgets in seconds per phase; each row sums to 1200.
  const BUDGETS = {
    1: { warmup: 120, sounds: 240, s2w: 240, phrases: 240, sentences: 180, talk: 150, wrap: 30 },
    2: { warmup: 150, sounds: 150, s2w: 180, phrases: 300, sentences: 240, talk: 150, wrap: 30 },
    3: { warmup: 150, sounds: 120, s2w: 120, phrases: 210, sentences: 330, talk: 240, wrap: 30 },
    4: { warmup: 150, sounds: 90, s2w: 90, phrases: 180, sentences: 300, talk: 360, wrap: 30 },
    5: { warmup: 180, sounds: 90, s2w: 60, phrases: 150, sentences: 300, talk: 390, wrap: 30 },
  };

  const BLOCK_INFO = {
    warmup: { title: "Warm-up", zh: "热身 · 复习" },
    sounds: { title: "Sound Lab", zh: "发音实验室" },
    s2w: { title: "IPA → Word", zh: "音标 → 单词" },
    phrases: { title: "Phrases", zh: "短语块" },
    sentences: { title: "Sentences", zh: "句子 · 影子跟读" },
    talk: { title: "Conversation", zh: "对话" },
    wrap: { title: "Wrap-up", zh: "收尾" },
  };

  const COACH = {
    intro1: {
      zh: "你好！我是你的英语教练。从今天开始，我们每天打二十分钟电话。你不用写字，只要跟着我的节奏：我说，你就大声说出来。听到“叮”的一声，就轮到你说了。说错没关系，大声最重要。准备好了吗？我们开始！",
      en: "Hi! I'm your English coach. Every day, we talk for twenty minutes. No writing. I speak, you speak. When you hear the beep, it's your turn. Ready? Let's go!",
    },
    warmDay1: { zh: "先热热身。张开嘴，大声跟我说。", en: "Warm up. Open your mouth and say it loud." },
    welcome: { zh: "欢迎回来！今天是第 {n} 天。", en: "Welcome back! This is day {n}." },
    theme: { zh: "今天的主题是：{zh}。", en: "Today's topic is: {title}." },
    review: { zh: "先复习。我说中文，你用英文说。想不起来没关系，我会告诉你。", en: "Quick review. I say it in Chinese, you say it in English." },
    sounds: { zh: "发音实验室。仔细听，然后大声模仿我。", en: "Sound lab. Listen carefully, then copy me." },
    pairs: { zh: "听两个词的区别，两个都跟我说。", en: "Listen to the difference. Say both." },
    pairQuiz: { zh: "听力小测验：我只说一个，你说是第一个还是第二个。", en: "Listening quiz. I say one word. Is it number one, or number two?" },
    s2w: { zh: "看音标，先自己读出来，然后听我说，再跟我说一遍。", en: "Look at the phonetics. Read it first. Then listen and repeat." },
    s2wRepeat: { zh: "再来一轮，听，然后跟我说。", en: "Again. Listen and repeat." },
    recall: { zh: "现在我说中文，你用英文说出来。", en: "Now I say it in Chinese. You say it in English." },
    phrases: { zh: "短语练习。先慢慢说，再用正常速度说。", en: "Phrases. First slowly, then at normal speed." },
    buildup: { zh: "长的我们从后往前，一点一点加长。", en: "Let's build it up, piece by piece, from the end." },
    fast: { zh: "加快速度，跟上我！", en: "Faster now. Keep up with me!" },
    sentences: { zh: "句子练习。一小块一小块地说，最后说完整的句子。", en: "Sentences. Small pieces first, then the whole sentence." },
    shadow: { zh: "影子跟读：我说第二遍的时候，你和我同时说。然后你自己再说一遍。", en: "Shadowing. The second time, speak with me, at the same time. Then say it alone." },
    talk: { zh: "现在我们聊天。我问你问题，你用英文回答。说错没关系，说出来就好。", en: "Now let's talk. I ask, you answer. Mistakes are okay. Just speak." },
    model: { zh: "你可以这样说：", en: "You can say:" },
    wrap: { zh: "二十分钟到了，你做得很好！最后，再说一遍今天的重点句。", en: "That's twenty minutes. Great job! One last time, today's key sentence." },
    bye: { zh: "明天同一时间，我们继续。拜拜！", en: "Same time tomorrow. Bye!" },
  };

  const WEEKDAYS = [
    ["Sunday", "星期日"], ["Monday", "星期一"], ["Tuesday", "星期二"], ["Wednesday", "星期三"],
    ["Thursday", "星期四"], ["Friday", "星期五"], ["Saturday", "星期六"],
  ];

  // ───────────── text helpers ─────────────

  /** Text suitable for TTS: no emphasis marks, thought-group slashes become commas, no "(n.)" notes. */
  function speakable(t) {
    return String(t)
      .replace(/\*/g, "")
      .replace(/\([^)]*\)/g, "")
      .replace(/\s*\/\s*/g, ", ")
      .replace(/…/g, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function wordCount(t) {
    return speakable(t).split(" ").filter(Boolean).length;
  }

  function fill(str, vars) {
    return String(str).replace(/\{(\w+)\}/g, (m, k) => (vars[k] !== undefined ? vars[k] : m));
  }

  function deepFill(obj, vars) {
    if (typeof obj === "string") return fill(obj, vars);
    if (Array.isArray(obj)) return obj.map((x) => deepFill(x, vars));
    if (obj && typeof obj === "object") {
      const out = {};
      for (const k of Object.keys(obj)) out[k] = deepFill(obj[k], vars);
      return out;
    }
    return obj;
  }

  /** Back-chaining: "Nice to meet you." -> ["meet you.", "to meet you.", "Nice to meet you."] */
  function backChain(text) {
    const w = String(text).replace(/\*/g, "").split(/\s+/).filter(Boolean);
    const n = w.length;
    if (n < 4) return [w.join(" ")];
    const step = n > 7 ? 3 : n > 5 ? 2 : 1;
    const sizes = [];
    for (let k = 2; k < n; k += step) sizes.push(k);
    sizes.push(n);
    return sizes.map((k) => w.slice(n - k).join(" "));
  }

  function splitSentences(text) {
    return String(text).split(/(?<=[.!?])\s+/).filter(Boolean);
  }

  function seeded(seed) {
    let s = (seed * 2654435761) >>> 0 || 1;
    return () => {
      s ^= s << 13; s >>>= 0;
      s ^= s >>> 17;
      s ^= s << 5; s >>>= 0;
      return s / 4294967296;
    };
  }

  function shuffle(arr, rng) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  // ───────────── speech scoring ─────────────

  const CONTRACTIONS = {
    "i'm": "i am", "it's": "it is", "what's": "what is", "that's": "that is", "where's": "where is",
    "he's": "he is", "she's": "she is", "you're": "you are", "we're": "we are", "they're": "they are",
    "don't": "do not", "doesn't": "does not", "didn't": "did not", "can't": "can not", "cannot": "can not",
    "i'll": "i will", "i'd": "i would", "i've": "i have", "let's": "let us", "it'll": "it will",
    "o'clock": "oclock", "isn't": "is not", "aren't": "are not", "won't": "will not",
  };
  const NUM = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"];
  const TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"];
  function numWord(n) {
    if (n < 20) return NUM[n];
    if (n < 100) return TENS[Math.floor(n / 10)] + (n % 10 ? " " + NUM[n % 10] : "");
    return String(n);
  }

  function normWords(s) {
    return String(s || "")
      .toLowerCase()
      .replace(/[’‘`]/g, "'")
      .replace(/\([^)]*\)/g, " ")
      .replace(/(\d+):00/g, "$1 oclock")
      .replace(/\d+/g, (d) => " " + numWord(parseInt(d, 10)) + " ")
      .replace(/-/g, " ")
      .split(/\s+/)
      .map((w) => w.replace(/[^a-z']/g, ""))
      .filter(Boolean)
      .map((w) => CONTRACTIONS[w] || w.replace(/'/g, ""))
      .join(" ")
      .split(" ")
      .filter(Boolean);
  }

  /** Fraction (0..1) of the expected words heard in order (LCS). */
  function scoreSpeech(expected, heard) {
    const a = normWords(speakable(expected));
    const b = normWords(heard);
    if (!a.length) return 1;
    if (!b.length) return 0;
    const dp = new Array(b.length + 1).fill(0);
    for (let i = 1; i <= a.length; i++) {
      let prev = 0;
      for (let j = 1; j <= b.length; j++) {
        const tmp = dp[j];
        dp[j] = a[i - 1] === b[j - 1] ? prev + 1 : Math.max(dp[j], dp[j - 1]);
        prev = tmp;
      }
    }
    return dp[b.length] / a.length;
  }

  /** Rough TTS duration, used by the simulator and as a watchdog in the browser. */
  function estimateSayMs(text, lang, rate) {
    if (lang === "zh") return 300 + String(text).replace(/\s/g, "").length * 240 / (rate || 1);
    return (300 + wordCount(text) * 380) / (rate || 1);
  }

  // ───────────── day content ─────────────

  function phaseOf(dayNum) {
    return C.PHASES.find((p) => dayNum >= p.from && dayNum <= p.to);
  }

  /** Day 31+: remix earlier days so the loop never ends. */
  function loopDay(dayNum) {
    const rng = seeded(dayNum * 7 + 3);
    const all = C.DAYS;
    const pick = (key, n) => shuffle(all.flatMap((d) => d[key]), rng).slice(0, n);
    const base = all[(dayNum - 31) % all.length];
    const cycle = Math.floor((dayNum - 31) / all.length) + 1;
    return {
      title: `Fluency Loop ${dayNum - 30}`,
      zh: `流利循环 · 第 ${cycle} 轮 · ${base.zh}`,
      focus: `${base.focus}（综合复习 + 更多自由对话）`,
      sounds: base.sounds,
      pairs: base.pairs,
      words: pick("words", 8),
      phrases: pick("phrases", 5),
      sentences: [...base.sentences.slice(0, 2), ...pick("sentences", 3)],
      talk: [...base.talk.slice(0, 2), ...pick("talk", 3)],
    };
  }

  function rawDay(dayNum) {
    return dayNum <= C.DAYS.length ? C.DAYS[dayNum - 1] : loopDay(dayNum);
  }

  function itemsOf(day) {
    return [
      ...day.phrases.map(([en, ipa, zh]) => ({ en, ipa, zh })),
      ...day.sentences.map(([en, zh]) => ({ en, zh })),
    ];
  }

  /** Spaced repetition: material from 1, 2, 4, 7, 14 and 30 days ago, weakest items first. */
  function reviewPool(dayNum, vars, weak, rng) {
    const out = [];
    const seen = new Set();
    const add = (it) => {
      if (!it.en || !it.zh || seen.has(it.en)) return;
      seen.add(it.en);
      out.push(it);
    };
    (weak || []).slice(0, 4).forEach((it) => add(deepFill(it, vars)));
    for (const back of [1, 2, 4, 7, 14, 30]) {
      const d = dayNum - back;
      if (d < 1) continue;
      const items = shuffle(itemsOf(deepFill(rawDay(d), vars)), rng);
      items.slice(0, back === 1 ? 4 : 2).forEach(add);
    }
    return out.slice(0, 12);
  }

  // ───────────── turn factory ─────────────

  function makeTurns(ctx) {
    const s = ctx.settings;
    const R = { slow: s.rate * 0.75, normal: s.rate, fast: Math.min(1.35, s.rate * 1.12) };
    const P = s.pause;
    const say = (text, r = "normal") => ({ t: "say", text: speakable(text), lang: "en", rate: R[r] });
    const sayZh = (text) => ({ t: "say", text, lang: "zh", rate: 1 });
    const show = (sh) => ({ t: "show", show: sh });
    const gap = (ms) => ({ t: "gap", ms });
    const repeatMs = (t) => Math.round((1400 + wordCount(t) * 620) * P);
    const recallMs = (t) => Math.round((3200 + wordCount(t) * 650) * P);
    const waitRepeat = (t) => ({ t: "wait", kind: "repeat", ms: repeatMs(t), expect: speakable(t) });
    const talkMs = Math.round(({ 1: 9000, 2: 10000, 3: 12000, 4: 14000, 5: 15000 }[ctx.phase.id]) * P);

    const H = {
      repeat: "跟我说 · Repeat",
      recall: "用英文说 · Say it in English",
      read: "读出音标 · Read the IPA",
      shadow: "一起说 · Speak with me",
      alone: "你自己说 · Your turn",
      answer: "用英文回答 · Answer",
      quiz: "第 1 个还是第 2 个？· One or two?",
      tip: "发音要点 · Tip",
      build: "一点点加长 · Build up",
    };

    const T = {
      coach(key, vars = {}) {
        const line = COACH[key];
        const lang = ctx.phase.coach;
        const text = fill(line[lang], vars);
        const other = fill(line[lang === "zh" ? "en" : "zh"], vars);
        return { show: { mode: "coach", main: text, zh: lang === "en" ? other : "" }, ops: [{ t: "say", text, lang, rate: lang === "en" ? R.normal : 1, coach: true }] };
      },

      tip(snd) {
        return { show: { mode: "tip", main: snd.label, zh: snd.tip, hint: H.tip }, ops: [sayZh(snd.tip)] };
      },

      repeat(it, r = "normal", opt = {}) {
        const ops = [say(it.en, r)];
        if (opt.withZh && it.zh) ops.push(sayZh(it.zh));
        ops.push(waitRepeat(it.en));
        return { item: it, show: { mode: "repeat", main: it.en, ipa: it.ipa, zh: it.zh, hint: H.repeat }, ops };
      },

      /** Slow, then normal speed, in one turn. */
      repeat2(it) {
        return {
          item: it,
          show: { mode: "repeat", main: it.en, ipa: it.ipa, zh: it.zh, hint: H.repeat },
          ops: [say(it.en, "slow"), waitRepeat(it.en), say(it.en, "normal"), waitRepeat(it.en)],
        };
      },

      recall(it) {
        return {
          item: it,
          show: { mode: "recall", main: "?", zh: it.zh, hint: H.recall },
          ops: [
            sayZh(it.zh),
            { t: "wait", kind: "recall", ms: recallMs(it.en), expect: speakable(it.en) },
            show({ mode: "repeat", main: it.en, ipa: it.ipa, zh: it.zh, hint: H.repeat }),
            say(it.en, "normal"),
            waitRepeat(it.en),
          ],
        };
      },

      ipaRead(it, withZh) {
        const ops = [
          { t: "wait", kind: "read", ms: Math.round((3200 + it.ipa.length * 120) * P), expect: it.en },
          show({ mode: "repeat", main: it.en, ipa: it.ipa, zh: it.zh, hint: H.repeat }),
          say(it.en, "normal"),
        ];
        if (withZh && it.zh) ops.push(sayZh(it.zh));
        ops.push(waitRepeat(it.en));
        return { item: it, show: { mode: "ipa", main: `/${it.ipa}/`, hint: H.read, ipaOnly: true }, ops };
      },

      pair([a, ia, b, ib]) {
        const both = `${speakable(a)}. ${speakable(b)}.`;
        return {
          show: { mode: "pair", main: `${a}   ·   ${b}`, ipa: `${ia}   ·   ${ib}`, hint: H.repeat },
          ops: [say(a, "slow"), gap(450), say(b, "slow"), waitRepeat(both), say(a), gap(300), say(b), waitRepeat(both)],
        };
      },

      quiz([a, ia, b, ib]) {
        const k = ctx.rng() < 0.5 ? 0 : 1;
        const word = k ? b : a;
        const num = k ? "two" : "one";
        return {
          show: { mode: "quiz", main: `1  ${a}      2  ${b}`, ipa: `1 /${ia}/      2 /${ib}/`, hint: H.quiz },
          ops: [
            say(word),
            { t: "wait", kind: "quiz", ms: Math.round(2800 * P), correct: [num, k ? "2" : "1", k ? "second" : "first", ...normWords(speakable(word))] },
            show({ mode: "repeat", main: `${k ? 2 : 1} · ${word}`, ipa: k ? ib : ia, hint: H.repeat }),
            say(`Number ${num}. ${speakable(word)}.`),
            waitRepeat(word),
          ],
        };
      },

      buildup(it) {
        const chunks = backChain(it.en);
        const ops = [];
        chunks.forEach((c, i) => {
          const last = i === chunks.length - 1;
          ops.push(show({ mode: "build", main: c, ipa: last ? it.ipa : "", zh: it.zh, hint: last ? H.repeat : H.build, full: it.en }));
          ops.push(say(c, last ? "normal" : "slow"), waitRepeat(c));
        });
        ops.push(say(it.en, "normal"), waitRepeat(it.en));
        return { item: it, show: { mode: "build", main: chunks[0], zh: it.zh, hint: H.build, full: it.en }, ops };
      },

      shadow(it, r = "normal") {
        return {
          item: it,
          show: { mode: "shadow", main: it.en, ipa: it.ipa, zh: it.zh, hint: H.shadow },
          ops: [
            say(it.en, r),
            gap(500),
            say(it.en, r),
            show({ mode: "repeat", main: it.en, ipa: it.ipa, zh: it.zh, hint: H.alone }),
            waitRepeat(it.en),
          ],
        };
      },

      talk([q, zh, model], round) {
        const parts = splitSentences(model);
        const ops = [say(q, "normal")];
        if (ctx.phase.coach === "zh" || round === 0) ops.push(sayZh(zh));
        ops.push({ t: "wait", kind: "free", ms: talkMs });
        const modelShow = { mode: "repeat", main: model, zh: `问：${q}`, hint: H.repeat };
        if (round === 0) {
          ops.push(show({ ...modelShow, hint: COACH.model.zh + " " + COACH.model.en }));
          const m = COACH.model[ctx.phase.coach];
          ops.push({ t: "say", text: m, lang: ctx.phase.coach, rate: ctx.phase.coach === "en" ? R.normal : 1, coach: true });
          for (const p of parts) ops.push(show({ ...modelShow, main: p, full: model }), say(p, "slow"), waitRepeat(p));
        } else {
          ops.push(show(modelShow));
          for (const p of parts) ops.push(say(p, "normal"), waitRepeat(p));
        }
        return { item: { en: model, zh }, show: { mode: "talk", main: q, zh, hint: H.answer }, ops };
      },
    };
    return T;
  }

  // ───────────── block generators ─────────────

  const ECHO = [
    ["Hello!", "həˈləʊ", "你好"], ["Hi!", "haɪ", "嗨"], ["Good morning!", "ɡʊd ˈmɔːnɪŋ", "早上好"],
    ["Okay.", "əʊˈkeɪ", "好的"], ["Yes.", "jes", "是"], ["No.", "nəʊ", "不"], ["Sorry.", "ˈsɒri", "对不起"],
    ["Thank you.", "ˈθæŋk juː", "谢谢"], ["See you!", "ˈsiː juː", "回见"], ["Goodbye!", "ɡʊdˈbaɪ", "再见"],
  ].map(([en, ipa, zh]) => ({ en, ipa, zh }));

  function* gWarmup(ctx) {
    const { T, day } = ctx;
    if (ctx.dayNum === 1) {
      yield T.coach("intro1");
      yield T.coach("warmDay1");
    } else {
      yield T.coach("welcome", { n: ctx.dayNum });
      yield T.coach("theme", { title: day.title, zh: day.zh });
    }
    if (ctx.review.length) {
      yield T.coach("review");
      for (;;) for (const it of ctx.review) yield T.recall(it);
    }
    for (let r = 0; ; r++) for (const it of ECHO) yield T.repeat(it, ["slow", "normal", "fast"][Math.min(r, 2)]);
  }

  function* gSounds(ctx) {
    const { T, day, rng } = ctx;
    if (!day.sounds.length) return;
    yield T.coach("sounds");
    for (let r = 0; ; r++) {
      for (const snd of day.sounds) {
        if (r === 0) yield T.tip(snd);
        for (const [text, ipa] of snd.ex) {
          const it = { en: text, ipa };
          if (r === 0) yield T.repeat2(it);
          else yield T.repeat(it, r >= 2 ? "fast" : "normal");
        }
      }
      if (day.pairs.length) {
        if (r === 0) {
          yield T.coach("pairs");
          for (const p of day.pairs) yield T.pair(p);
        } else {
          if (r === 1) yield T.coach("pairQuiz");
          for (const p of shuffle(day.pairs, rng)) yield T.quiz(p);
        }
      }
    }
  }

  function* gS2W(ctx) {
    const { T, day, rng } = ctx;
    const words = day.words.map(([en, ipa, zh]) => ({ en, ipa, zh }));
    if (!words.length) return;
    yield T.coach("s2w");
    for (let r = 0; ; r++) {
      const list = r === 0 ? words : shuffle(words, rng);
      const mode = r % 3;
      if (r > 0 && mode === 0) yield T.coach("s2w");
      if (mode === 1) yield T.coach("s2wRepeat");
      if (mode === 2) yield T.coach("recall");
      for (const w of list) {
        if (mode === 0) yield T.ipaRead(w, r === 0);
        else if (mode === 1) yield T.repeat(w, "normal", { withZh: true });
        else yield T.recall(w);
      }
    }
  }

  function* gPhrases(ctx) {
    const { T, day, rng } = ctx;
    const items = day.phrases.map(([en, ipa, zh]) => ({ en, ipa, zh }));
    if (!items.length) return;
    yield T.coach("phrases");
    for (const it of items) yield T.repeat2(it);
    yield T.coach("buildup");
    for (const it of items) yield wordCount(it.en) >= 4 ? T.buildup(it) : T.repeat(it, "normal");
    yield T.coach("recall");
    for (const it of shuffle(items, rng)) yield T.recall(it);
    for (let r = 0; ; r++) {
      if (r % 2 === 0) {
        yield T.coach("fast");
        for (const it of items) yield T.repeat(it, "fast");
      } else {
        yield T.coach("recall");
        for (const it of shuffle(items, rng)) yield T.recall(it);
      }
    }
  }

  function* gSentences(ctx) {
    const { T, day, rng } = ctx;
    const items = day.sentences.map(([en, zh]) => ({ en, zh }));
    if (!items.length) return;
    yield T.coach("sentences");
    for (const it of items) yield T.buildup(it);
    yield T.coach("shadow");
    for (const it of items) yield T.shadow(it);
    yield T.coach("recall");
    for (const it of shuffle(items, rng)) yield T.recall(it);
    for (let r = 0; ; r++) {
      if (r % 2 === 0) {
        yield T.coach("fast");
        for (const it of items) yield T.shadow(it, "fast");
      } else {
        yield T.coach("recall");
        for (const it of shuffle(items, rng)) yield T.recall(it);
      }
    }
  }

  function* gTalk(ctx) {
    const { T, day, rng } = ctx;
    if (!day.talk.length) return;
    yield T.coach("talk");
    for (let r = 0; ; r++) {
      const list = r < 2 ? day.talk : shuffle(day.talk, rng);
      for (const q of list) yield T.talk(q, r);
    }
  }

  function* gWrap(ctx) {
    const { T, day } = ctx;
    const [en, zh] = day.sentences[0];
    yield T.coach("wrap");
    yield T.repeat({ en, zh }, "normal");
    yield T.coach("bye");
  }

  const GENERATORS = { warmup: gWarmup, sounds: gSounds, s2w: gS2W, phrases: gPhrases, sentences: gSentences, talk: gTalk, wrap: gWrap };

  function describe(key, day) {
    switch (key) {
      case "warmup": return "打招呼 + 间隔复习之前学过的内容";
      case "sounds": return day.sounds.map((x) => x.label).join("  ") + (day.pairs.length ? "  ·  对比：" + day.pairs.map((p) => `${p[0]}/${p[2]}`).join(", ") : "");
      case "s2w": return "看音标说单词：" + day.words.map((w) => w[0]).join(", ");
      case "phrases": return day.phrases.map((p) => p[0]).join("  ·  ");
      case "sentences": return day.sentences.map((p) => p[0]).join("  ·  ");
      case "talk": return day.talk.map((p) => p[0]).join("  ·  ");
      case "wrap": return "重点句 + 明天见";
      default: return "";
    }
  }

  // ───────────── public builder ─────────────

  const DEFAULT_SETTINGS = { name: "Alex", city: "Shanghai", rate: 0.9, pause: 1.0 };

  /**
   * @param {number} dayNum 1-based
   * @param {object} settings { name, city, rate, pause }
   * @param {object} [opts] { weak: [{en, zh, ipa}], date: Date }
   */
  function buildSession(dayNum, settings, opts = {}) {
    const st = { ...DEFAULT_SETTINGS, ...(settings || {}) };
    const date = opts.date || new Date();
    const [weekday, weekdayZh] = WEEKDAYS[date.getDay()];
    const vars = { name: st.name || DEFAULT_SETTINGS.name, city: st.city || DEFAULT_SETTINGS.city, weekday, weekdayZh };
    const phase = phaseOf(dayNum);
    const day = deepFill(rawDay(dayNum), vars);
    const rng = seeded(dayNum * 1000 + date.getDate());
    const ctx = { dayNum, day, phase, settings: st, rng, review: reviewPool(dayNum, vars, opts.weak, rng) };
    ctx.T = makeTurns(ctx);

    const budget = BUDGETS[phase.id];
    const blocks = Object.keys(budget).map((key) => ({
      key,
      ...BLOCK_INFO[key],
      seconds: budget[key],
      desc: describe(key, day),
      mustFinish: key === "wrap",
      turns: () => GENERATORS[key](ctx),
    }));

    return { dayNum, day, phase, blocks, totalSeconds: SESSION_SECONDS, review: ctx.review };
  }

  const api = {
    buildSession, scoreSpeech, normWords, estimateSayMs, speakable, backChain, phaseOf,
    BUDGETS, SESSION_SECONDS, DEFAULT_SETTINGS, COACH, totalDays: C.DAYS.length,
  };
  root.DEC = root.DEC || {};
  root.DEC.session = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
