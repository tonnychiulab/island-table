(function () {
  var ENTRANCE_FALLBACK = "幕後人：走岔一步不要緊，肯回頭便是正道。";

  function scriptBase() {
    var scripts = document.getElementsByTagName("script");
    var src = "";
    for (var i = scripts.length - 1; i >= 0; i--) {
      if (scripts[i].src && /game\.js(\?|$)/.test(scripts[i].src)) {
        src = scripts[i].src;
        break;
      }
    }
    if (!src && document.currentScript && document.currentScript.src) {
      src = document.currentScript.src;
    }
    return src.replace(/game\.js(\?.*)?$/, "");
  }

  function applyBox(el, spec) {
    el.style.left = spec.left + "px";
    el.style.top = spec.top + "px";
    el.style.background = spec.color;
    if (spec.width) el.style.width = spec.width + "px";
    if (spec.height) el.style.height = spec.height + "px";
    if (spec.fontSize) el.style.fontSize = spec.fontSize + "px";
    if (spec.textColor) el.style.color = spec.textColor;
  }

  function findLevel(data, id) {
    for (var i = 0; i < data.levels.length; i++) {
      if (data.levels[i].id === id) return data.levels[i];
    }
    return null;
  }

  function boot(level, entranceText) {
    var ORDER = level.nodes.map(function (n) { return n.id; });
    var selected = [];
    var phase = "play";
    var okTimer = null;
    var nodeEls = {};

    var stage = document.getElementById("stage");
    var routeLine = document.getElementById("route-line");
    var messageEl = document.getElementById("message");
    var btnReset = document.getElementById("btn-reset");
    var btnGo = document.getElementById("btn-go");
    var btnRetry = document.getElementById("btn-retry");
    var btnAgain = document.getElementById("btn-again");
    var fullscreenBtn = document.getElementById("fullscreen-btn");
    var titleEl = document.getElementById("level-title");
    var nodesHost = document.getElementById("nodes");

    if (titleEl) titleEl.textContent = level.title;
    document.title = "島嶼餐桌 · " + level.title;

    var startEl = document.createElement("div");
    startEl.className = "node start";
    startEl.id = level.start.id;
    startEl.setAttribute("data-id", level.start.id);
    startEl.setAttribute("aria-label", level.start.label);
    startEl.textContent = level.start.label;
    applyBox(startEl, level.start);
    nodesHost.appendChild(startEl);
    nodeEls[level.start.id] = startEl;

    level.nodes.forEach(function (n) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "node";
      btn.id = n.id;
      btn.setAttribute("data-id", n.id);
      btn.setAttribute("aria-label", n.label);
      btn.textContent = n.label;
      applyBox(btn, n);
      nodesHost.appendChild(btn);
      nodeEls[n.id] = btn;
    });

    function clearFx() {
      ORDER.forEach(function (id) {
        nodeEls[id].classList.remove("shake", "bright");
      });
      var dots = stage.querySelectorAll(".fx-dot");
      for (var i = 0; i < dots.length; i++) dots[i].parentNode.removeChild(dots[i]);
      if (okTimer) {
        clearTimeout(okTimer);
        okTimer = null;
      }
    }

    function shakeOnce(el) {
      el.classList.remove("shake");
      void el.offsetWidth;
      el.classList.add("shake");
    }

    function centerOf(el) {
      return {
        x: el.offsetLeft + el.offsetWidth / 2,
        y: el.offsetTop + el.offsetHeight / 2
      };
    }

    function scaleStage() {
      var w = window.innerWidth;
      var h = window.innerHeight;
      var s = Math.min(w / 1280, h / 720);
      stage.style.transform = "scale(" + s + ")";
    }

    function drawRoute() {
      var pts = [centerOf(nodeEls[level.start.id])];
      for (var i = 0; i < selected.length; i++) {
        pts.push(centerOf(nodeEls[selected[i]]));
      }
      routeLine.setAttribute(
        "points",
        pts.map(function (p) { return p.x + "," + p.y; }).join(" ")
      );
    }

    function setMessage(text, kind) {
      messageEl.innerHTML = "";
      if (!text) {
        messageEl.className = "";
        messageEl.classList.remove("visible");
        return;
      }
      if (kind === "fail") {
        var lead = document.createElement("div");
        lead.className = "msg-line";
        lead.textContent = entranceText;
        var science = document.createElement("div");
        science.className = "msg-line";
        science.textContent = text;
        messageEl.appendChild(lead);
        messageEl.appendChild(science);
      } else {
        messageEl.textContent = text;
      }
      messageEl.className = "visible " + (kind || "");
    }

    function syncButtons() {
      var playing = phase === "play" || phase === "hint";
      btnReset.classList.toggle("hidden", !playing);
      btnGo.classList.toggle("hidden", !playing);
      btnRetry.classList.toggle("hidden", phase !== "fail");
      btnAgain.classList.toggle("hidden", phase !== "success");
    }

    function clearRouteKeepMap() {
      selected = [];
      phase = "play";
      ORDER.forEach(function (id) {
        nodeEls[id].classList.remove("selected");
      });
      clearFx();
      setMessage("");
      drawRoute();
      syncButtons();
    }

    function selectNode(id) {
      if (phase !== "play" && phase !== "hint") return;
      if (selected.indexOf(id) !== -1) return;
      selected.push(id);
      nodeEls[id].classList.add("selected");
      if (phase === "hint") {
        phase = "play";
        setMessage("");
      }
      drawRoute();
      syncButtons();
    }

    function playSeedAwayThenOk() {
      var correctId = null;
      for (var i = 0; i < level.nodes.length; i++) {
        if (level.nodes[i].role === "correct") {
          correctId = level.nodes[i].id;
          break;
        }
      }
      var from = centerOf(nodeEls[correctId]);
      var dot = document.createElement("div");
      dot.className = "fx-dot";
      dot.style.left = from.x + "px";
      dot.style.top = from.y + "px";
      stage.appendChild(dot);
      void dot.offsetWidth;
      dot.style.left = from.x + 160 + "px";
      dot.style.top = from.y - 90 + "px";
      okTimer = setTimeout(function () {
        okTimer = null;
        if (phase === "success") setMessage(level.success, "ok");
      }, 780);
    }

    function playPollenOntoFlowerThenOk() {
      var correctId = null;
      for (var i = 0; i < level.nodes.length; i++) {
        if (level.nodes[i].role === "correct") {
          correctId = level.nodes[i].id;
          break;
        }
      }
      var from = centerOf(nodeEls[level.start.id]);
      var to = centerOf(nodeEls[correctId]);
      var dot = document.createElement("div");
      dot.className = "fx-dot pollen";
      dot.style.left = from.x + "px";
      dot.style.top = from.y + "px";
      stage.appendChild(dot);
      void dot.offsetWidth;
      dot.style.left = to.x + "px";
      dot.style.top = to.y + "px";
      okTimer = setTimeout(function () {
        okTimer = null;
        if (phase === "success") setMessage(level.success, "ok");
      }, 780);
    }

    function runSuccessMotion() {
      if (level.successMotion === "brighten") {
        level.nodes.forEach(function (n) {
          if (n.role === "correct") nodeEls[n.id].classList.add("bright");
        });
        setMessage(level.success, "ok");
        return;
      }
      setMessage("");
      if (level.successMotion === "seed") playSeedAwayThenOk();
      else if (level.successMotion === "pollen") playPollenOntoFlowerThenOk();
      else setMessage(level.success, "ok");
    }

    function judgePotPair() {
      var missingParts = [];
      var required = [];
      for (var i = 0; i < level.nodes.length; i++) {
        if (level.nodes[i].role === "correct") required.push(level.nodes[i].id);
      }
      for (var j = 0; j < required.length; j++) {
        if (selected.indexOf(required[j]) === -1) {
          missingParts.push(level.missing[required[j]]);
        }
      }
      if (missingParts.length) {
        phase = "hint";
        setMessage(missingParts.join("。") + "。", "hint");
        syncButtons();
        return;
      }

      var hasBear = false;
      var hasPot = false;
      var potEl = null;
      for (var k = 0; k < level.nodes.length; k++) {
        var n = level.nodes[k];
        if (n.role === "bear" && selected.indexOf(n.id) !== -1) hasBear = true;
        if (n.role === "pot" && selected.indexOf(n.id) !== -1) {
          hasPot = true;
          potEl = nodeEls[n.id];
        }
      }

      if (hasBear && hasPot) {
        phase = "fail";
        clearFx();
        if (potEl) shakeOnce(potEl);
        setMessage(level.failureScience, "fail");
        syncButtons();
        return;
      }

      phase = "success";
      clearFx();
      runSuccessMotion();
      syncButtons();
    }

    function judgeWrongNode() {
      var correctId = null;
      var wrongId = null;
      for (var i = 0; i < level.nodes.length; i++) {
        if (level.nodes[i].role === "correct") correctId = level.nodes[i].id;
        if (level.nodes[i].role === "wrong") wrongId = level.nodes[i].id;
      }
      var hasCorrect = selected.indexOf(correctId) !== -1;
      var hasWrong = selected.indexOf(wrongId) !== -1;

      if (!hasCorrect && !hasWrong) {
        phase = "hint";
        setMessage(level.missing, "hint");
        syncButtons();
        return;
      }

      if (hasWrong) {
        phase = "fail";
        clearFx();
        shakeOnce(nodeEls[wrongId]);
        setMessage(level.failureScience, "fail");
        syncButtons();
        return;
      }

      phase = "success";
      clearFx();
      runSuccessMotion();
      syncButtons();
    }

    function launch() {
      if (phase !== "play" && phase !== "hint") return;
      if (level.rule === "potPair") judgePotPair();
      else judgeWrongNode();
    }

    ORDER.forEach(function (id) {
      nodeEls[id].addEventListener("click", function () {
        selectNode(id);
      });
    });

    btnReset.addEventListener("click", function () {
      if (phase === "play" || phase === "hint") clearRouteKeepMap();
    });
    btnGo.addEventListener("click", launch);
    btnRetry.addEventListener("click", clearRouteKeepMap);
    btnAgain.addEventListener("click", clearRouteKeepMap);

    fullscreenBtn.addEventListener("click", function () {
      var root = document.documentElement;
      if (!document.fullscreenElement) {
        if (root.requestFullscreen) root.requestFullscreen();
        else if (root.webkitRequestFullscreen) root.webkitRequestFullscreen();
      } else {
        if (document.exitFullscreen) document.exitFullscreen();
        else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
      }
    });

    window.addEventListener("resize", scaleStage);
    scaleStage();
    drawRoute();
    syncButtons();

    window.__islandTable = {
      select: selectNode,
      launch: launch,
      reset: clearRouteKeepMap,
      getSelected: function () { return selected.slice(); },
      getPhase: function () { return phase; },
      getMessage: function () { return messageEl.textContent; },
      ENTRANCE_TEXT: entranceText,
      FAIL_TEXT: level.failureScience,
      OK_TEXT: level.success,
      MISS_TEXT: typeof level.missing === "string" ? level.missing : null,
      levelId: level.id,
      rule: level.rule,
      successMotion: level.successMotion
    };
  }

  var TEACHER_TEAL = "#0f766e";
  var MAX_TEACHER_HASH = 3500;

  function showBootError(text) {
    var msg = document.getElementById("message");
    if (msg) {
      msg.className = "visible fail";
      msg.textContent = text;
    }
  }

  function levelFromTeacherPayload(p) {
    return {
      id: "teacher",
      title: p.a,
      start: {
        id: "animal",
        label: p.a,
        color: TEACHER_TEAL,
        left: 80,
        top: 270,
        width: 200,
        height: 200,
        fontSize: 36
      },
      nodes: [
        {
          id: "correct",
          label: p.c,
          role: "correct",
          color: "#2e8b57",
          left: 520,
          top: 180
        },
        {
          id: "wrong",
          label: p.w,
          role: "wrong",
          color: "#8b5a2b",
          left: 900,
          top: 360
        }
      ],
      rule: "wrongNode",
      success: p.s,
      failureScience: p.f,
      missing: "還缺" + p.c + "。",
      successMotion: "seed"
    };
  }

  function parseTeacherHash(hash) {
    var raw = (hash || "").replace(/^#/, "");
    if (!raw) {
      return { error: "empty" };
    }
    if (raw.length > MAX_TEACHER_HASH) {
      return { error: "oversize" };
    }
    var data;
    try {
      data = JSON.parse(decodeURIComponent(raw));
    } catch (e) {
      return { error: "bad" };
    }
    if (!data || typeof data !== "object") return { error: "bad" };
    var keys = ["a", "c", "w", "s", "f"];
    var out = {};
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      var v = data[k];
      if (typeof v !== "string" || !v.trim()) return { error: "bad" };
      out[k] = v.trim();
    }
    return { payload: out };
  }

  function bootFromHash() {
    var parsed = parseTeacherHash(location.hash);
    if (parsed.error === "oversize") {
      showBootError("句子太長了，請回到出題頁改短一點再產生網址。");
      return;
    }
    if (parsed.error) {
      showBootError("網址不完整或無法讀取。請用出題頁重新產生連結。");
      return;
    }
    boot(levelFromTeacherPayload(parsed.payload), ENTRANCE_FALLBACK);
  }

  if (document.body.getAttribute("data-from-hash") === "1") {
    bootFromHash();
    window.addEventListener("hashchange", function () {
      location.reload();
    });
    return;
  }

  var levelId = document.body.getAttribute("data-level-id");
  if (!levelId) {
    console.error("Missing data-level-id on body");
    return;
  }

  var base = scriptBase();
  fetch(base + "levels.json")
    .then(function (res) {
      if (!res.ok) throw new Error("levels.json HTTP " + res.status);
      return res.json();
    })
    .then(function (data) {
      var level = findLevel(data, levelId);
      if (!level) throw new Error("Unknown level id: " + levelId);
      boot(level, data.entranceText || ENTRANCE_FALLBACK);
    })
    .catch(function (err) {
      console.error(err);
      showBootError("關卡資料載入失敗。請用靜態伺服器開啟 site/。");
    });
})();
