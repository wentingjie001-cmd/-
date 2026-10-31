(function () {
  const { session: S, engine: E, speech: SP, curriculum: C } = window.DEC;
  const $ = (id) => document.getElementById(id);
  const STORE = "dec.v1";

  // ───────────── persistence ─────────────

  const DEFAULTS = {
    settings: { name: "", city: "", rate: 0.9, pause: 1.0, voiceURI: "", listen: SP.canListen, cue: true, showText: true },
    progress: { day: 1, streak: 0, lastDate: null, done: {}, minutes: 0, sessions: [], weak: [] },
  };

  function load() {
    try {
      const raw = JSON.parse(localStorage.getItem(STORE) || "{}");
      return {
        settings: { ...DEFAULTS.settings, ...(raw.settings || {}) },
        progress: { ...DEFAULTS.progress, ...(raw.progress || {}) },
      };
    } catch (e) {
      return JSON.parse(JSON.stringify(DEFAULTS));
    }
  }
  const state = load();
  const save = () => localStorage.setItem(STORE, JSON.stringify({ settings: state.settings, progress: state.progress }));

  const ymd = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const today = () => ymd(new Date());
  const yesterday = () => ymd(new Date(Date.now() - 864e5));

  let viewDay = state.progress.day;

  // ───────────── helpers ─────────────

  function esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }
  /** *word* -> stressed, " / " -> visible thought-group bar */
  function rich(s) {
    return esc(s).replace(/\*([^*]+)\*/g, '<strong class="stress">$1</strong>').replace(/\s\/\s/g, ' <span class="sep">/</span> ');
  }
  const mmss = (ms) => {
    const s = Math.max(0, Math.floor(ms / 1000));
    return `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
  };
  const sessionSettings = () => ({
    name: state.settings.name.trim() || "Alex",
    city: state.settings.city.trim() || "Shanghai",
    rate: state.settings.rate,
    pause: state.settings.pause,
  });
  const build = (n) => S.buildSession(n, sessionSettings(), { weak: state.progress.weak });

  // ───────────── home ─────────────

  function renderHome() {
    const p = state.progress;
    const sess = build(viewDay);
    const d = sess.day;
    $("streak").textContent = p.streak ? `连续 ${p.streak} 天` : "今天开始打卡";
    $("phasePill").textContent = sess.phase.zh;
    $("phasePill").dataset.phase = sess.phase.id;
    $("dayLabel").textContent = `第 ${viewDay} 天`;
    $("dayTitle").textContent = `· ${d.zh}`;
    $("dayFocus").textContent = `发音重点：${d.focus}`;
    $("prevDay").disabled = viewDay <= 1;

    const doneDate = p.done[viewDay];
    const note = $("doneNote");
    if (doneDate) {
      note.hidden = false;
      note.textContent = doneDate === today()
        ? "今天这一课已完成！可以再练一遍，明天会自动进入下一天。"
        : `这一课已在 ${doneDate} 完成，可以随时再练。`;
    } else if (viewDay !== p.day) {
      note.hidden = false;
      note.textContent = viewDay > p.day ? `你的进度在第 ${p.day} 天，这一天可以提前预习。` : "复习之前的一天。";
    } else {
      note.hidden = true;
    }

    $("plan").innerHTML = sess.blocks
      .map((b) => `
        <li>
          <div class="plan-min">${b.seconds >= 60 ? (b.seconds / 60).toFixed(b.seconds % 60 ? 1 : 0) + " 分钟" : b.seconds + " 秒"}</div>
          <div class="plan-body">
            <div class="plan-name">${esc(b.zh)}</div>
            <div class="plan-desc">${rich(b.desc)}</div>
          </div>
        </li>`)
      .join("");

    $("phases").innerHTML = C.PHASES.slice(0, 4)
      .map((ph) => `<div class="phase" data-phase="${ph.id}"><b>第 ${ph.from}–${ph.to} 天</b><span>${esc(ph.zh.replace(/^第.阶段：/, ""))}</span></div>`)
      .join("");

    const cells = [];
    for (let n = 1; n <= 30; n++) {
      const ph = S.phaseOf(n).id;
      const cls = [p.done[n] ? "done" : "", n === p.day ? "current" : "", n === viewDay ? "viewing" : ""].join(" ");
      cells.push(`<button class="cell ${cls}" data-phase="${ph}" data-day="${n}" title="${esc(C.DAYS[n - 1].zh)}">${n}</button>`);
    }
    $("roadmap").innerHTML = cells.join("");
  }

  function checkEnvironment() {
    const warn = [];
    if (callError) warn.push(callError);
    if (!SP.canSpeak) warn.push("这个浏览器不支持语音朗读。请用 Chrome、Edge 或 Safari 打开。");
    else if (!SP.englishVoices().length) warn.push("没有找到英文语音。请在系统设置里安装英文语音包，或换 Chrome 浏览器。");
    if (SP.canSpeak && !SP.zh) warn.push("没有找到中文语音：中文提示会以字幕显示（不朗读）。");
    if (!SP.canListen) warn.push("这个浏览器不支持语音识别：教练会按固定节奏留出时间给你说，不会听你的发音。推荐用 Chrome。");
    $("envWarn").hidden = !warn.length;
    $("envWarn").innerHTML = warn.map(esc).join("<br>");
  }

  // ───────────── call ─────────────

  let engine = null;
  let callInProgress = false;
  let callError = "";
  let tick = null;
  let wakeLock = null;
  let current = null;
  let session = null;

  function show(scr) {
    for (const id of ["home", "call", "done"]) $(id).hidden = id !== scr;
    window.scrollTo(0, 0);
  }

  function renderCue(sh) {
    current = sh || current;
    if (!current) return;
    const sh2 = current;
    const textOn = state.settings.showText;
    const card = $("cueCard");
    card.dataset.mode = sh2.mode || "";
    $("cHint").textContent = sh2.hint || (sh2.mode === "coach" ? "教练" : "");
    const hideText = !textOn && !sh2.ipaOnly && sh2.mode !== "coach";
    $("cMain").innerHTML = hideText ? '<span class="listen-only">仔细听</span>' : rich(sh2.main || "");
    $("cMain").classList.toggle("long", (sh2.main || "").length > 42);
    $("cIpa").textContent = !hideText && sh2.ipa ? (sh2.ipa.startsWith("/") || sh2.mode === "pair" || sh2.mode === "quiz" ? sh2.ipa : `/${sh2.ipa}/`) : "";
    $("cZh").textContent = textOn || sh2.mode === "recall" || sh2.mode === "tip" ? sh2.zh || "" : "";
    $("heard").textContent = "";
    $("heard").className = "heard";
  }

  function setState(st, ms) {
    const wrap = $("avatarWrap");
    wrap.dataset.state = st;
    const label = { coach: "教练在说，请听", you: "轮到你说", idle: "", paused: "已暂停" }[st] || "";
    $("stateLabel").textContent = label;
    const circle = $("youRing").querySelector("circle");
    circle.style.animation = "none";
    if (st === "you" && ms) {
      void circle.getBoundingClientRect();
      circle.style.animation = `drain ${ms}ms linear forwards`;
    }
  }

  function renderSegments(activeIdx) {
    const total = session.blocks.reduce((a, b) => a + b.seconds, 0);
    $("segments").innerHTML = session.blocks
      .map((b, i) => `<div class="seg ${i < activeIdx ? "past" : i === activeIdx ? "active" : ""}" style="flex:${b.seconds / total}" title="${esc(b.zh)}"><i></i></div>`)
      .join("");
  }

  async function startCall() {
    // Lock synchronously, before microphone/wake-lock permission promises yield.
    if (callInProgress) return;
    callInProgress = true;
    $("startBtn").disabled = true;
    try {
      callError = "";
      checkEnvironment();
      SP.unlock();
      SP.cueEnabled = state.settings.cue;
      SP.listenEnabled = state.settings.listen && SP.canListen;
      SP.pickVoices(state.settings.voiceURI);
      if (SP.listenEnabled && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          stream.getTracks().forEach((t) => t.stop());
        } catch (e) {
          SP.listenEnabled = false;
        }
      }
      try { wakeLock = navigator.wakeLock ? await navigator.wakeLock.request("screen") : null; } catch (e) { wakeLock = null; }

      session = build(viewDay);
      $("tglText").checked = state.settings.showText;
      $("tglMic").checked = SP.listenEnabled;
      $("tglMic").disabled = !SP.canListen;
      show("call");

      const io = {
        now: () => performance.now(),
        say: (t, l, r) => SP.say(t, l, r || state.settings.rate),
        listen: (ms, o) => SP.listen(ms, o),
        sleep: (ms) => SP.sleep(ms),
        cancel: () => SP.cancel(),
        cue: () => SP.cue(),
        show: (sh) => renderCue(sh),
        onBlock: (i, b) => {
          $("callBlock").textContent = b.zh;
          renderSegments(i);
        },
        onHeard: (t, score) => {
          const h = $("heard");
          h.textContent = `我听到：${t}`;
          h.className = "heard " + (score >= 0.75 ? "good" : score >= 0.5 ? "ok" : "low");
        },
      };
      SP.onState = (st, ms) => setState(st, ms);
      SP.onInterim = (t) => {
        const h = $("heard");
        h.textContent = `我听到：${t}`;
        h.className = "heard live";
      };
      SP.onMicError = () => {
        $("tglMic").checked = false;
        $("heard").textContent = "麦克风没有权限，已切换为固定节奏模式。";
      };

      engine = new E.Engine(session, io);
      tick = setInterval(() => {
        if (!engine) return;
        $("callTime").textContent = mmss(engine.elapsed());
      }, 250);
      const stats = await engine.run();
      endCall(stats);
    } catch (e) {
      if (engine) engine.stop();
      show("home");
      callError = "通话未能正常启动或继续，请重试。";
      checkEnvironment();
    } finally {
      clearInterval(tick);
      tick = null;
      SP.cancel();
      SP.onState = null;
      SP.onInterim = null;
      SP.onMicError = null;
      if (wakeLock) wakeLock.release().catch(() => {});
      wakeLock = null;
      engine = null;
      callInProgress = false;
      $("startBtn").disabled = false;
    }
  }

  function endCall(stats) {
    const minutes = stats.elapsedMs / 60000;
    // Reaching the final block (stats.completed) can also mean skipping it.
    // Only actual, unpaused practice time earns completion credit.
    const completed = minutes >= 18;
    const p = state.progress;
    const dayNum = session.dayNum;
    p.minutes = Math.round((p.minutes + minutes) * 10) / 10;
    p.sessions.push({ date: today(), day: dayNum, minutes: Math.round(minutes * 10) / 10, completed, heard: stats.heard, good: stats.good });
    if (p.sessions.length > 400) p.sessions = p.sessions.slice(-400);
    if (completed) {
      if (p.lastDate !== today()) {
        p.streak = p.lastDate === yesterday() ? p.streak + 1 : 1;
        p.lastDate = today();
      }
      p.done[dayNum] = today();
      if (dayNum >= p.day) p.day = dayNum + 1;
    }
    const weakNew = stats.weak.filter((w) => !p.weak.some((x) => x.en === w.en));
    p.weak = [...weakNew, ...p.weak].slice(0, 20);
    save();

    $("doneBadge").textContent = completed ? "✓" : "…";
    $("doneBadge").className = "done-badge" + (completed ? "" : " partial");
    $("doneTitle").textContent = completed ? `第 ${dayNum} 天完成！` : `第 ${dayNum} 天 · 练了 ${minutes.toFixed(1)} 分钟`;
    $("doneSub").textContent = completed
      ? `明天继续第 ${p.day} 天：${S.buildSession(p.day, sessionSettings()).day.zh}。同一时间，效果最好。`
      : "这次没有完成全部 20 分钟，进度保留在这一天。下次从头再来一遍吧。";
    const acc = stats.heard ? Math.round((stats.good / stats.heard) * 100) + "%" : "—";
    $("doneStats").innerHTML = [
      ["本次", `${minutes.toFixed(1)} 分钟`],
      ["开口次数", stats.turns],
      ["说得好", stats.heard ? acc : "未开麦"],
      ["连续打卡", `${p.streak} 天`],
      ["累计", `${Math.round(p.minutes)} 分钟`],
    ].map(([k, v]) => `<div><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join("");
    $("weakWrap").hidden = !stats.weak.length;
    $("weakList").innerHTML = stats.weak.map((w) => `<li><b>${esc(w.en)}</b><span>${esc(w.zh)}</span></li>`).join("");
    viewDay = p.day;
    show("done");
  }

  function togglePause() {
    if (!engine) return;
    if (engine.paused) {
      engine.resume();
      $("pauseIcon").textContent = "❚❚";
      $("pauseText").textContent = "暂停";
    } else {
      engine.pause();
      setState("paused");
      $("pauseIcon").textContent = "▶";
      $("pauseText").textContent = "继续";
    }
  }

  // ───────────── settings ─────────────

  function openSettings() {
    const s = state.settings;
    $("sName").value = s.name;
    $("sCity").value = s.city;
    $("sRate").value = s.rate;
    $("sPause").value = s.pause;
    $("sRateOut").textContent = `${s.rate.toFixed(2)}×`;
    $("sPauseOut").textContent = `${s.pause.toFixed(1)}×`;
    $("sListen").checked = s.listen && SP.canListen;
    $("sListen").disabled = !SP.canListen;
    $("sCue").checked = s.cue;
    $("sText").checked = s.showText;
    const en = SP.englishVoices();
    SP.pickVoices(s.voiceURI);
    $("sVoice").innerHTML = en.length
      ? en.map((v) => `<option value="${esc(v.voiceURI)}" ${SP.en && v.voiceURI === SP.en.voiceURI ? "selected" : ""}>${esc(v.name)} (${esc(v.lang)})</option>`).join("")
      : '<option value="">（没有找到英文语音）</option>';
    $("sZhVoice").textContent = SP.zh ? `中文提示语音：${SP.zh.name}` : "没有中文语音，中文提示只显示字幕";
    $("settings").showModal();
  }

  function readSettings() {
    const s = state.settings;
    s.name = $("sName").value.trim();
    s.city = $("sCity").value.trim();
    s.rate = parseFloat($("sRate").value);
    s.pause = parseFloat($("sPause").value);
    s.voiceURI = $("sVoice").value;
    s.listen = $("sListen").checked;
    s.cue = $("sCue").checked;
    s.showText = $("sText").checked;
    save();
    SP.pickVoices(s.voiceURI);
  }

  // ───────────── wiring ─────────────

  $("prevDay").onclick = () => { viewDay = Math.max(1, viewDay - 1); renderHome(); };
  $("nextDay").onclick = () => { viewDay += 1; renderHome(); };
  $("roadmap").onclick = (e) => {
    const n = e.target.dataset && e.target.dataset.day;
    if (n) { viewDay = parseInt(n, 10); renderHome(); }
  };
  $("startBtn").onclick = () => startCall();
  $("backHome").onclick = () => { renderHome(); show("home"); };

  $("btnPause").onclick = togglePause;
  $("btnRepeat").onclick = () => engine && engine.repeat();
  $("btnSkip").onclick = () => engine && engine.skip();
  $("btnNextBlock").onclick = () => engine && engine.nextBlock();
  $("btnHangup").onclick = () => {
    if (engine && confirm("结束今天的通话？不满 18 分钟不算完成。")) engine.stop();
  };
  $("tglText").onchange = (e) => { state.settings.showText = e.target.checked; save(); renderCue(); };
  $("tglMic").onchange = (e) => { state.settings.listen = e.target.checked; SP.listenEnabled = e.target.checked && SP.canListen; save(); };

  document.addEventListener("keydown", (e) => {
    if (!engine || $("call").hidden || e.target.tagName === "INPUT") return;
    if (e.code === "Space") { e.preventDefault(); togglePause(); }
    else if (e.key === "r" || e.key === "R") engine.repeat();
    else if (e.key === "ArrowRight") engine.skip();
    else if (e.key === "n" || e.key === "N") engine.nextBlock();
  });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden && engine && !engine.paused) togglePause();
  });

  $("openSettings").onclick = openSettings;
  $("sRate").oninput = (e) => ($("sRateOut").textContent = `${parseFloat(e.target.value).toFixed(2)}×`);
  $("sPause").oninput = (e) => ($("sPauseOut").textContent = `${parseFloat(e.target.value).toFixed(1)}×`);
  $("settings").addEventListener("close", () => { readSettings(); renderHome(); checkEnvironment(); });
  $("sTest").onclick = () => {
    SP.unlock();
    SP.pickVoices($("sVoice").value);
    SP.cancel();
    SP.say("Hello! I'm your English coach. Let's practise together.", "en", parseFloat($("sRate").value))
      .then((r) => !r.aborted && SP.say("你好，我是你的英语教练。", "zh"));
  };
  $("sReset").onclick = () => {
    if (!confirm("确定要清除所有进度吗？")) return;
    state.progress = JSON.parse(JSON.stringify(DEFAULTS.progress));
    save();
    viewDay = 1;
    $("settings").close();
  };

  renderHome();
  SP.loadVoices().then(() => {
    SP.pickVoices(state.settings.voiceURI);
    checkEnvironment();
  });
})();
