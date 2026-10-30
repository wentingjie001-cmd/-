/*
 * Plays a session built by session.js through an IO adapter.
 *
 * IO adapter interface (browser: speech.js + app.js, tests: tools/simulate.js):
 *   now()                          -> ms
 *   say(text, lang, rate)          -> Promise<{ aborted }>
 *   listen(ms, { kind, expect })   -> Promise<{ aborted, transcript }>
 *   sleep(ms)                      -> Promise<{ aborted }>
 *   cancel()                       aborts the pending say/listen/sleep
 *   cue()                          short "your turn" beep (optional)
 *   show(display)                  update the screen
 *   onBlock(index, block, window)  (optional)
 *   onHeard(transcript, score)     (optional)
 */
(function (root) {
  const S =
    typeof module !== "undefined" && module.exports && typeof require === "function"
      ? require("./session.js")
      : root.DEC.session;

  const PRAISE = ["Good!", "Nice!", "Great!", "Very good!", "Well done!", "Perfect!"];
  const MIN_BLOCK_SHARE = 0.4;

  class Engine {
    constructor(session, io) {
      this.session = session;
      this.io = io;
      this.paused = false;
      this.stopped = false;
      this.cmd = null;
      this.pausedMs = 0;
      this.pauseStart = 0;
      this.resumeWaiters = [];
      this.praiseIdx = 0;
      this.goodStreak = 0;
      this.stats = { turns: 0, heard: 0, good: 0, weak: [], blocks: [] };
    }

    elapsed() {
      const live = this.paused ? this.io.now() - this.pauseStart : 0;
      return this.io.now() - this.startAt - this.pausedMs - live;
    }

    pause() {
      if (this.paused || this.stopped) return;
      this.paused = true;
      this.pauseStart = this.io.now();
      this.io.cancel();
    }

    resume() {
      if (!this.paused) return;
      this.pausedMs += this.io.now() - this.pauseStart;
      this.paused = false;
      this.resumeWaiters.splice(0).forEach((f) => f());
    }

    /** Skip the current turn. */
    skip() {
      if (this.paused) return;
      this.cmd = "skip";
      this.io.cancel();
    }

    /** Replay the current turn from the start. */
    repeat() {
      if (this.paused) return;
      this.cmd = "repeat";
      this.io.cancel();
    }

    /** Jump to the next block. */
    nextBlock() {
      if (this.paused) return;
      this.cmd = "block";
      this.io.cancel();
    }

    stop() {
      this.stopped = true;
      this.io.cancel();
      this.resumeWaiters.splice(0).forEach((f) => f());
    }

    gate() {
      if (!this.paused || this.stopped) return Promise.resolve();
      return new Promise((r) => this.resumeWaiters.push(r));
    }

    interrupted() {
      return this.paused || this.stopped || this.cmd !== null;
    }

    async run() {
      this.startAt = this.io.now();
      let deadline = 0;
      const blocks = this.session.blocks;
      for (let i = 0; i < blocks.length; i++) {
        const b = blocks[i];
        const start = this.elapsed();
        deadline += b.seconds * 1000;
        const end = Math.max(deadline, start + b.seconds * 1000 * MIN_BLOCK_SHARE);
        if (this.io.onBlock) this.io.onBlock(i, b, { start, end, deadline });
        const gen = b.turns();
        let first = true;
        for (;;) {
          if (this.stopped) return this.finish(false);
          if (!b.mustFinish && !first && this.elapsed() >= end) break;
          const { value, done } = gen.next();
          if (done) break;
          first = false;
          const res = await this.playTurn(value);
          if (this.stopped) return this.finish(false);
          if (res === "block") break;
        }
        this.stats.blocks.push({ key: b.key, ms: this.elapsed() - start });
      }
      return this.finish(true);
    }

    finish(completed) {
      this.stats.completed = completed;
      this.stats.elapsedMs = this.elapsed();
      return this.stats;
    }

    async playTurn(turn) {
      for (;;) {
        await this.gate();
        if (this.stopped) return "stop";
        this.io.show(turn.show);
        const res = await this.playOps(turn);
        if (res === "ok") {
          this.stats.turns++;
          return "ok";
        }
        if (this.stopped) return "stop";
        const cmd = this.cmd;
        this.cmd = null;
        if (cmd === "skip") return "skip";
        if (cmd === "block") return "block";
        // paused or "repeat": replay the whole turn once resumed
      }
    }

    async playOps(turn) {
      let lastSay = null;
      for (const op of turn.ops) {
        if (this.interrupted()) return "int";
        if (op.t === "show") {
          this.io.show(op.show);
        } else if (op.t === "gap") {
          if ((await this.io.sleep(op.ms)).aborted) return "int";
        } else if (op.t === "say") {
          if (op.lang === "en" && !op.coach) lastSay = op;
          if ((await this.io.say(op.text, op.lang, op.rate)).aborted) return "int";
        } else if (op.t === "wait") {
          if ((await this.doWait(op, lastSay, turn)) === "int") return "int";
        }
      }
      return "ok";
    }

    async listen(op) {
      if (this.io.cue) this.io.cue();
      return this.io.listen(op.ms, { kind: op.kind, expect: op.expect });
    }

    nextPraise() {
      return PRAISE[this.praiseIdx++ % PRAISE.length];
    }

    markWeak(item) {
      if (item && item.en && item.zh && !this.stats.weak.some((w) => w.en === item.en)) {
        this.stats.weak.push({ en: item.en, zh: item.zh, ipa: item.ipa || "" });
      }
    }

    async doWait(op, lastSay, turn) {
      const r = await this.listen(op);
      if (r.aborted) return "int";
      if (!r.transcript) return "ok";
      this.stats.heard++;

      if (op.kind === "free") {
        const n = S.normWords(r.transcript).length;
        if (this.io.onHeard) this.io.onHeard(r.transcript, n >= 3 ? 1 : 0.5);
        if (n >= 2) {
          this.stats.good++;
          return (await this.io.say(this.nextPraise(), "en")).aborted ? "int" : "ok";
        }
        return "ok";
      }

      if (op.kind === "quiz") {
        const heard = S.normWords(r.transcript);
        const right = op.correct.some((c) => heard.includes(String(c).toLowerCase()));
        if (this.io.onHeard) this.io.onHeard(r.transcript, right ? 1 : 0);
        if (right) this.stats.good++;
        return (await this.io.say(right ? "Right!" : "Not quite.", "en")).aborted ? "int" : "ok";
      }

      const score = S.scoreSpeech(op.expect, r.transcript);
      if (this.io.onHeard) this.io.onHeard(r.transcript, score);

      if (score >= 0.75) {
        this.stats.good++;
        this.goodStreak++;
        // Praise occasionally so the rhythm stays tight.
        if (this.goodStreak % 3 === 0) {
          if ((await this.io.say(this.nextPraise(), "en")).aborted) return "int";
        }
        return "ok";
      }
      this.goodStreak = 0;
      if (op.kind === "recall") {
        this.markWeak(turn.item);
        return "ok";
      }
      if (op.kind === "repeat" && score < 0.5 && lastSay) {
        this.markWeak(turn.item);
        if ((await this.io.say("Once more.", "en")).aborted) return "int";
        if ((await this.io.say(lastSay.text, "en", lastSay.rate * 0.9)).aborted) return "int";
        const r2 = await this.listen(op);
        if (r2.aborted) return "int";
        if (r2.transcript) {
          const s2 = S.scoreSpeech(op.expect, r2.transcript);
          if (this.io.onHeard) this.io.onHeard(r2.transcript, s2);
          if (s2 >= 0.75) {
            this.stats.good++;
            if ((await this.io.say("Better!", "en")).aborted) return "int";
          }
        }
      }
      return "ok";
    }
  }

  const api = { Engine, PRAISE };
  root.DEC = root.DEC || {};
  root.DEC.engine = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
