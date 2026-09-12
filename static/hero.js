/* DNNR Tech — hero particle scene: "Daily needs, naturally refined."
   Grey particles drift (daily needs), rush together and take on the logo's colors to form
   the DNNR mark (naturally refined), hold, then burst and drift again. ~6 s per cycle.
   Debug: ?pcT=<ms> renders the deterministic state at that time (used for screenshots). */
(function () {
  'use strict';
  var root = document.querySelector('.pc-scene');
  if (!root) return;
  var canvas = root.querySelector('canvas');
  var ctx = canvas.getContext('2d');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fixedT = Number(new URLSearchParams(location.search).get('pcT')) || 0;

  var PHASES = [['drift', 1300], ['form', 1300], ['hold', 2200], ['burst', 1000]];
  var CYCLE = PHASES.reduce(function (s, p) { return s + p[1]; }, 0);
  var FRAME = 1000 / 60;

  var W = 0, H = 0, DPR = 1, parts = [], visible = true;
  var pointer = { x: -1e4, y: -1e4, active: false };
  var grey = [138, 141, 153];
  var seed = 7;
  function rand() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }

  function readGrey() {
    var c = getComputedStyle(document.documentElement).getPropertyValue('--faint').trim();
    var m = /^#([0-9a-f]{6})$/i.exec(c);
    if (m) grey = [parseInt(m[1].slice(0, 2), 16), parseInt(m[1].slice(2, 4), 16), parseInt(m[1].slice(4, 6), 16)];
  }
  function ease(t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }

  function build(img) {
    var rect = root.getBoundingClientRect();
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = rect.width; H = rect.height;
    canvas.width = Math.round(W * DPR); canvas.height = Math.round(H * DPR);
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);

    var targetW = W * 0.78, scale = targetW / img.width;
    var off = document.createElement('canvas');
    off.width = Math.round(targetW); off.height = Math.round(img.height * scale);
    var o = off.getContext('2d');
    o.drawImage(img, 0, 0, off.width, off.height);
    var data = o.getImageData(0, 0, off.width, off.height).data;
    var step = Math.max(5, Math.round(W / 78));
    var ox = (W - off.width) / 2, oy = (H - off.height) / 2 - H * 0.03;
    var pts = [];
    for (var y = 0; y < off.height; y += step) {
      for (var x = 0; x < off.width; x += step) {
        var i = (y * off.width + x) * 4;
        if (data[i + 3] > 150) pts.push([ox + x, oy + y, data[i], data[i + 1], data[i + 2]]);
      }
    }
    seed = 7;
    parts = pts.map(function (q) {
      return { hx: q[0], hy: q[1], r: q[2], g: q[3], b: q[4], size: step * 0.82,
               x: rand() * W, y: rand() * H * 0.86, sx: 0, sy: 0, ph: rand() * 6.283, amp: 8 + rand() * 18,
               vx: 0, vy: 0, fx: 0, fy: 0, dx: 0, dy: 0, spin: rand() < .5 ? 1 : -1 };
    });
    parts.forEach(function (p) { p.sx = p.x; p.sy = p.y; });
    readGrey();
  }

  function phaseAt(ms) {
    var t = ms % CYCLE, acc = 0;
    for (var i = 0; i < PHASES.length; i++) {
      if (t < acc + PHASES[i][1]) return { name: PHASES[i][0], k: (t - acc) / PHASES[i][1] };
      acc += PHASES[i][1];
    }
    return { name: 'drift', k: 0 };
  }

  var lastPhase = '';
  // Advance simulation to time ms (monotonic) and return render positions.
  function step(ms) {
    var ph = reduce ? { name: 'hold', k: .5 } : phaseAt(ms);
    var sec = ms / 1000;
    if (ph.name !== lastPhase) {
      root.dataset.phase = ph.name;
      if (ph.name === 'form') parts.forEach(function (p) { p.fx = p.x; p.fy = p.y; });
      if (ph.name === 'burst') parts.forEach(function (p) {
        var ang = Math.atan2(p.y - H / 2, p.x - W / 2) + (rand() - .5) * 1.1;
        var sp = 4 + rand() * 9;
        p.vx = Math.cos(ang) * sp; p.vy = Math.sin(ang) * sp;
      });
      if (ph.name === 'drift') parts.forEach(function (p) { p.sx = p.x; p.sy = p.y; });
      lastPhase = ph.name;
    }
    for (var i = 0; i < parts.length; i++) {
      var p = parts[i], x, y;
      if (ph.name === 'drift') {
        x = p.sx + Math.cos(sec * 1.4 + p.ph) * p.amp; y = p.sy + Math.sin(sec * 1.2 + p.ph * 1.3) * p.amp; p.mix = 0;
      } else if (ph.name === 'form') {
        var e = ease(ph.k), swirl = Math.sin(Math.PI * ph.k) * 60 * p.spin;
        var nx = -(p.hy - p.fy), ny = p.hx - p.fx, len = Math.hypot(nx, ny) || 1;
        x = p.fx + (p.hx - p.fx) * e + nx / len * swirl; y = p.fy + (p.hy - p.fy) * e + ny / len * swirl; p.mix = Math.min(1, e * 1.2);
      } else if (ph.name === 'hold') {
        x = p.hx + Math.cos(sec * 2 + i) * .7; y = p.hy + Math.sin(sec * 2.3 + i) * .7; p.mix = 1;
      } else {
        p.vx *= .92; p.vy *= .92; p.fx = (p.fx === undefined ? p.x : p.fx);
        x = p.x + p.vx; y = p.y + p.vy; p.mix = 1 - ease(ph.k);
      }
      var ddx = x - pointer.x, ddy = y - pointer.y, d2 = ddx * ddx + ddy * ddy, R = 80;
      if (pointer.active && d2 < R * R) {
        var dl = Math.sqrt(d2) || 1, f = (1 - dl / R) * 22;
        p.dx += (ddx / dl * f - p.dx) * .25; p.dy += (ddy / dl * f - p.dy) * .25;
      } else { p.dx *= .88; p.dy *= .88; }
      p.x = x; p.y = y; p.rx = x + p.dx; p.ry = y + p.dy;
    }
    return ph;
  }

  function draw(ph) {
    ctx.clearRect(0, 0, W, H);
    for (var i = 0; i < parts.length; i++) {
      var p = parts[i], m = p.mix;
      ctx.globalAlpha = .38 + .62 * m;
      ctx.fillStyle = 'rgb(' + ((grey[0] + (p.r - grey[0]) * m) | 0) + ',' + ((grey[1] + (p.g - grey[1]) * m) | 0) + ',' + ((grey[2] + (p.b - grey[2]) * m) | 0) + ')';
      var s = p.size * (.7 + .3 * m);
      ctx.beginPath(); ctx.arc(p.rx, p.ry, s / 2, 0, 6.2832); ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  var start = 0, simT = 0;
  function loop(now) {
    if (!start) start = now;
    if (visible) {
      var target = now - start;
      // Fixed-step simulation keeps motion identical across frame rates.
      while (simT + FRAME <= target) { simT += FRAME; var ph = step(simT); }
      if (ph) draw(ph);
    } else { start = now - simT; }
    requestAnimationFrame(loop);
  }

  var img = new Image();
  img.onload = function () {
    build(img);
    if (fixedT) { var ph; for (var t = 0; t <= fixedT; t += FRAME) ph = step(t); draw(ph); return; }
    if (reduce) { draw(step(0)); return; }
    requestAnimationFrame(loop);
  };
  img.src = root.dataset.logo;

  var rt;
  window.addEventListener('resize', function () {
    clearTimeout(rt);
    rt = setTimeout(function () { if (!img.complete) return; build(img); lastPhase = ''; simT = 0; start = 0; if (reduce || fixedT) draw(step(fixedT || 0)); }, 150);
  });
  var mq = window.matchMedia('(prefers-color-scheme: dark)');
  if (mq.addEventListener) mq.addEventListener('change', readGrey);
  root.addEventListener('pointermove', function (e) { var r = canvas.getBoundingClientRect(); pointer.x = e.clientX - r.left; pointer.y = e.clientY - r.top; pointer.active = true; });
  root.addEventListener('pointerleave', function () { pointer.active = false; });
  if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(root);
  document.addEventListener('visibilitychange', function () { visible = !document.hidden; });
})();
