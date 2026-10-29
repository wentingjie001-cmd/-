/*
 * Browser IO for the engine: Web Speech API text-to-speech + speech recognition,
 * plus a WebAudio "your turn" cue. Every pending operation can be aborted by cancel().
 */
(function (root) {
  const S = root.DEC.session;
  const Rec = root.SpeechRecognition || root.webkitSpeechRecognition;
  const synth = root.speechSynthesis;

  const Speech = {
    canSpeak: !!synth,
    canListen: !!Rec,
    listenEnabled: false,
    cueEnabled: true,
    voices: [],
    en: null,
    zh: null,
    pending: new Set(),
    onState: null,     // (state: "coach" | "you" | "idle", ms?) => void
    onInterim: null,   // (text) => void
    onMicError: null,  // (code) => void
    _keep: null,
    _ctx: null,

    loadVoices() {
      return new Promise((resolve) => {
        if (!synth) return resolve([]);
        const got = () => {
          const v = synth.getVoices();
          if (v.length) {
            this.voices = v;
            resolve(v);
            return true;
          }
          return false;
        };
        if (got()) return;
        synth.addEventListener("voiceschanged", () => got(), { once: true });
        setTimeout(() => resolve((this.voices = synth.getVoices())), 2500);
      });
    },

    englishVoices() {
      return this.voices.filter((v) => /^en/i.test(v.lang));
    },

    pickVoices(preferredURI) {
      const en = this.englishVoices();
      const score = (v) =>
        (/en[-_]GB/i.test(v.lang) ? 4 : /en[-_]US/i.test(v.lang) ? 3 : 1) +
        (/google|natural|neural|premium|enhanced|siri/i.test(v.name) ? 3 : 0) +
        (v.localService ? 0 : 1);
      this.en = en.find((v) => v.voiceURI === preferredURI) || en.slice().sort((a, b) => score(b) - score(a))[0] || null;
      const zh = this.voices.filter((v) => /^zh/i.test(v.lang) || /cmn/i.test(v.lang));
      this.zh =
        zh.find((v) => /zh[-_]CN/i.test(v.lang) && /google|natural|neural|ting|xiao/i.test(v.name)) ||
        zh.find((v) => /zh[-_]CN|cmn/i.test(v.lang)) ||
        zh[0] ||
        null;
    },

    /** Must be called from a user gesture (Start button) so audio is unlocked. */
    unlock() {
      try {
        if (!this._ctx) this._ctx = new (root.AudioContext || root.webkitAudioContext)();
        if (this._ctx.state === "suspended") this._ctx.resume();
      } catch (e) { /* no WebAudio: cue stays silent */ }
      if (synth) {
        const u = new SpeechSynthesisUtterance(" ");
        u.volume = 0;
        synth.speak(u);
      }
    },

    track(abort) {
      this.pending.add(abort);
      return () => this.pending.delete(abort);
    },

    sleep(ms) {
      return new Promise((resolve) => {
        let untrack;
        const t = setTimeout(() => { untrack(); resolve({ aborted: false }); }, ms);
        untrack = this.track(() => { clearTimeout(t); untrack(); resolve({ aborted: true }); });
      });
    },

    say(text, lang = "en", rate) {
      if (!text) return Promise.resolve({ aborted: false });
      // Without a Chinese voice the line is shown as a subtitle only; give time to read it.
      if (!synth || (lang === "zh" && !this.zh)) {
        if (this.onState) this.onState("coach");
        const ms = lang === "zh" ? Math.min(7000, 800 + text.length * 160) : S.estimateSayMs(text, lang, rate || 1);
        return this.sleep(ms);
      }
      return new Promise((resolve) => {
        const u = new SpeechSynthesisUtterance(text);
        const voice = lang === "zh" ? this.zh : this.en;
        if (voice) u.voice = voice;
        u.lang = voice ? voice.lang : lang === "zh" ? "zh-CN" : "en-GB";
        u.rate = rate || 0.9;
        this._keep = u; // Chrome drops onend if the utterance is garbage-collected
        let done = false;
        let untrack = () => {};
        const finish = (aborted) => {
          if (done) return;
          done = true;
          clearTimeout(watchdog);
          untrack();
          resolve({ aborted });
        };
        const watchdog = setTimeout(() => finish(false), S.estimateSayMs(text, lang, u.rate) * 2.5 + 3000);
        untrack = this.track(() => finish(true));
        u.onend = () => finish(false);
        u.onerror = () => finish(false);
        if (this.onState) this.onState("coach");
        synth.resume();
        synth.speak(u);
      });
    },

    cue() {
      if (!this.cueEnabled || !this._ctx) return;
      try {
        const ctx = this._ctx;
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.type = "sine";
        o.frequency.value = 880;
        g.gain.setValueAtTime(0.0001, ctx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.12, ctx.currentTime + 0.015);
        g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.14);
        o.connect(g).connect(ctx.destination);
        o.start();
        o.stop(ctx.currentTime + 0.16);
      } catch (e) { /* ignore */ }
    },

    /**
     * The learner's turn. Always lasts up to `ms`; with recognition on it ends early
     * once a full utterance has been heard, so the rhythm follows the learner.
     */
    listen(ms, { kind } = {}) {
      return new Promise((resolve) => {
        if (this.onState) this.onState("you", ms);
        let done = false;
        let transcript = "";
        let rec = null;
        let settle = null;
        let untrack = () => {};
        const finish = (aborted) => {
          if (done) return;
          done = true;
          clearTimeout(timer);
          clearTimeout(settle);
          untrack();
          if (rec) {
            rec.onresult = rec.onerror = rec.onend = null;
            try { rec.abort(); } catch (e) { /* already stopped */ }
          }
          resolve({ aborted, transcript: aborted ? "" : transcript.trim() });
        };
        const useRec = this.listenEnabled && Rec;
        const timer = setTimeout(() => finish(false), ms + (useRec ? 700 : 0));
        untrack = this.track(() => finish(true));
        if (!useRec) return;

        rec = new Rec();
        rec.lang = "en-US";
        rec.interimResults = true;
        rec.continuous = kind === "free";
        rec.maxAlternatives = 1;
        rec.onresult = (e) => {
          let t = "";
          for (let i = 0; i < e.results.length; i++) t += e.results[i][0].transcript + " ";
          transcript = t;
          if (this.onInterim) this.onInterim(t.trim());
          const last = e.results[e.results.length - 1];
          clearTimeout(settle);
          if (last.isFinal) settle = setTimeout(() => finish(false), kind === "free" ? 1800 : 300);
        };
        rec.onerror = (e) => {
          if (e.error === "not-allowed" || e.error === "service-not-allowed") {
            this.listenEnabled = false;
            if (this.onMicError) this.onMicError(e.error);
          }
        };
        rec.onend = () => {
          if (transcript) finish(false);
        };
        try { rec.start(); } catch (e) { /* keep timed pause */ }
      });
    },

    cancel() {
      if (synth) synth.cancel();
      [...this.pending].forEach((abort) => abort());
      this.pending.clear();
    },
  };

  root.DEC.speech = Speech;
})(window);
