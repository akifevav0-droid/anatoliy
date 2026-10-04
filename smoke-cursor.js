/*
  Курсор сайта Анатолия Шабаршова: точка 8 px + мягкий «дым» за ней (WebGL).
  Работает только на компьютере (экран от 1024 px, мышь), без «уменьшить движение».
  Нет WebGL — остаётся только точка, без ошибок.

  Симуляция жидкости — сокращённая версия WebGL Fluid Simulation:

  MIT License

  Copyright (c) 2017 Pavel Dobryakov

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
*/
(function () {
  'use strict';

  var desktop = window.matchMedia('(min-width: 1024px) and (pointer: fine)').matches;
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!desktop || calm) return;

  var config = {
    SIM_RESOLUTION: 64,
    DYE_RESOLUTION: 512,
    DENSITY_DISSIPATION: 3,             // след тает примерно за полсекунды
    VELOCITY_DISSIPATION: 2,
    PRESSURE: 0.8,
    PRESSURE_ITERATIONS: 20,
    CURL: 3,
    SPLAT_RADIUS: 0.05,                 // тонкий «пар» за точкой, не облако
    SPLAT_FORCE: 1500,
    MAX_ALPHA: 0.2,                       // пар не плотнее 0,2 и только тонкой струйкой — текст читается
    COLOR_A: [30 / 255, 160 / 255, 220 / 255],  // #1EA0DC — голубая вода бассейна
    COLOR_B: [110 / 255, 205 / 255, 240 / 255]  // #6ECDF0 — светлая бирюза
  };
  var HOVER = 'a, button, [role="button"], summary, .card, [data-card], [data-cursor]';
  var me = document.currentScript;
  var withDot = !(me && me.getAttribute('data-dot') === 'off'); // на сайте точку рисует сама страница

  // ---------- точка ----------
  var hover = false;
  if (withDot) {
    var style = document.createElement('style');
    style.textContent =
      'html.sh-cursor, html.sh-cursor * { cursor: none !important; }' +
      'html.sh-cursor input, html.sh-cursor textarea, html.sh-cursor select { cursor: auto !important; }' +
      '.sh-dot { position: fixed; left: 0; top: 0; width: 8px; height: 8px; margin: -4px 0 0 -4px; border-radius: 50%;' +
      ' background: #34466F; pointer-events: none; z-index: 10001; will-change: transform;' +
      ' transition: width .25s ease, height .25s ease, margin .25s ease, background-color .25s ease, opacity .2s ease; }' +
      '.sh-dot.is-hover { width: 28px; height: 28px; margin: -14px 0 0 -14px; background: rgba(143,164,209,.35);' +
      ' box-shadow: inset 0 0 0 1.5px #34466F; }' +
      '.sh-dot.is-hidden { opacity: 0; }' +
      '.sh-smoke { position: fixed; inset: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 10000; }';
    document.head.appendChild(style);

    var dot = document.createElement('div');
    dot.className = 'sh-dot is-hidden';
    document.body.appendChild(dot);
    document.documentElement.classList.add('sh-cursor'); // стрелку прячем только после запуска скрипта

    document.addEventListener('mousemove', function (e) {
      dot.style.transform = 'translate3d(' + e.clientX + 'px,' + e.clientY + 'px,0)';
      dot.classList.remove('is-hidden');
      var t = e.target;
      var field = t.closest && t.closest('input, textarea, select');
      dot.classList.toggle('is-hidden', !!field);
      hover = !!(t.closest && t.closest(HOVER));
      dot.classList.toggle('is-hover', hover);
    }, { passive: true });
    document.addEventListener('mouseleave', function () { dot.classList.add('is-hidden'); });

  } else {
    var style0 = document.createElement('style');
    style0.textContent = '.sh-smoke { position: fixed; inset: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 50; }';
    document.head.appendChild(style0);
    document.addEventListener('mousemove', function (e) {
      hover = !!(e.target && e.target.closest && e.target.closest(HOVER));
    }, { passive: true });
  }

  // ---------- дым ----------
  var canvas = document.createElement('canvas');
  canvas.className = 'sh-smoke';
  canvas.setAttribute('aria-hidden', 'true');
  var webgl = null;
  try { webgl = getWebGLContext(canvas); } catch (err) { webgl = null; }
  if (!webgl || !webgl.ext.formatRGBA) return;           // нет WebGL — только точка
  document.body.appendChild(canvas);
  var gl = webgl.gl, ext = webgl.ext;

  function pixelRatio() { return Math.min(window.devicePixelRatio || 1, 2); }
  function scaled(v) { return Math.floor(v * pixelRatio()); }

  function getWebGLContext(cv) {
    var params = { alpha: true, depth: false, stencil: false, antialias: false, preserveDrawingBuffer: false, premultipliedAlpha: true };
    var g = cv.getContext('webgl2', params);
    var isWebGL2 = !!g;
    if (!isWebGL2) g = cv.getContext('webgl', params) || cv.getContext('experimental-webgl', params);
    if (!g) return null;
    var halfFloat, linear;
    if (isWebGL2) {
      g.getExtension('EXT_color_buffer_float');
      linear = g.getExtension('OES_texture_float_linear');
    } else {
      halfFloat = g.getExtension('OES_texture_half_float');
      linear = g.getExtension('OES_texture_half_float_linear');
      if (!halfFloat) return null;
    }
    g.clearColor(0, 0, 0, 0);
    var type = isWebGL2 ? g.HALF_FLOAT : halfFloat.HALF_FLOAT_OES;
    var rgba, rg, r;
    if (isWebGL2) {
      rgba = supportedFormat(g, g.RGBA16F, g.RGBA, type);
      rg = supportedFormat(g, g.RG16F, g.RG, type);
      r = supportedFormat(g, g.R16F, g.RED, type);
    } else {
      rgba = rg = r = supportedFormat(g, g.RGBA, g.RGBA, type);
    }
    return { gl: g, ext: { formatRGBA: rgba, formatRG: rg, formatR: r, halfFloatTexType: type, supportLinearFiltering: !!linear } };
  }

  function supportedFormat(g, internalFormat, format, type) {
    if (!renderable(g, internalFormat, format, type)) {
      if (internalFormat === g.R16F) return supportedFormat(g, g.RG16F, g.RG, type);
      if (internalFormat === g.RG16F) return supportedFormat(g, g.RGBA16F, g.RGBA, type);
      return null;
    }
    return { internalFormat: internalFormat, format: format };
  }

  function renderable(g, internalFormat, format, type) {
    var tex = g.createTexture();
    g.bindTexture(g.TEXTURE_2D, tex);
    g.texParameteri(g.TEXTURE_2D, g.TEXTURE_MIN_FILTER, g.NEAREST);
    g.texParameteri(g.TEXTURE_2D, g.TEXTURE_MAG_FILTER, g.NEAREST);
    g.texParameteri(g.TEXTURE_2D, g.TEXTURE_WRAP_S, g.CLAMP_TO_EDGE);
    g.texParameteri(g.TEXTURE_2D, g.TEXTURE_WRAP_T, g.CLAMP_TO_EDGE);
    g.texImage2D(g.TEXTURE_2D, 0, internalFormat, 4, 4, 0, format, type, null);
    var fbo = g.createFramebuffer();
    g.bindFramebuffer(g.FRAMEBUFFER, fbo);
    g.framebufferTexture2D(g.FRAMEBUFFER, g.COLOR_ATTACHMENT0, g.TEXTURE_2D, tex, 0);
    return g.checkFramebufferStatus(g.FRAMEBUFFER) === g.FRAMEBUFFER_COMPLETE;
  }

  function compile(type, source, keywords) {
    if (keywords) source = keywords.map(function (k) { return '#define ' + k + '\n'; }).join('') + source;
    var s = gl.createShader(type);
    gl.shaderSource(s, source);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
    return s;
  }

  function Program(vs, fs) {
    var p = gl.createProgram();
    gl.attachShader(p, vs);
    gl.attachShader(p, fs);
    gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    this.program = p;
    this.uniforms = {};
    var n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
    for (var i = 0; i < n; i++) {
      var name = gl.getActiveUniform(p, i).name;
      this.uniforms[name] = gl.getUniformLocation(p, name);
    }
  }
  Program.prototype.bind = function () { gl.useProgram(this.program); };

  var baseVS = compile(gl.VERTEX_SHADER, [
    'precision highp float;',
    'attribute vec2 aPosition;',
    'varying vec2 vUv, vL, vR, vT, vB;',
    'uniform vec2 texelSize;',
    'void main () {',
    '  vUv = aPosition * 0.5 + 0.5;',
    '  vL = vUv - vec2(texelSize.x, 0.0); vR = vUv + vec2(texelSize.x, 0.0);',
    '  vT = vUv + vec2(0.0, texelSize.y); vB = vUv - vec2(0.0, texelSize.y);',
    '  gl_Position = vec4(aPosition, 0.0, 1.0);',
    '}'].join('\n'));

  var copyFS = compile(gl.FRAGMENT_SHADER, [
    'precision mediump float; precision mediump sampler2D;',
    'varying highp vec2 vUv; uniform sampler2D uTexture;',
    'void main () { gl_FragColor = texture2D(uTexture, vUv); }'].join('\n'));

  var clearFS = compile(gl.FRAGMENT_SHADER, [
    'precision mediump float; precision mediump sampler2D;',
    'varying highp vec2 vUv; uniform sampler2D uTexture; uniform float value;',
    'void main () { gl_FragColor = value * texture2D(uTexture, vUv); }'].join('\n'));

  // вывод на прозрачный холст: цвет дыма из палитры, непрозрачность не выше MAX_ALPHA
  var displayFS = compile(gl.FRAGMENT_SHADER, [
    'precision highp float; precision highp sampler2D;',
    'varying vec2 vUv; uniform sampler2D uTexture; uniform float maxAlpha;',
    'void main () {',
    '  vec3 c = max(texture2D(uTexture, vUv).rgb, vec3(0.0));',
    '  float m = max(c.r, max(c.g, c.b));',
    '  vec3 hue = m > 0.0001 ? c / m : vec3(0.0);',
    '  float a = maxAlpha * clamp(m * 2.0, 0.0, 1.0);',
    '  gl_FragColor = vec4(hue * a, a);',
    '}'].join('\n'));

  var splatFS = compile(gl.FRAGMENT_SHADER, [
    'precision highp float; precision highp sampler2D;',
    'varying vec2 vUv; uniform sampler2D uTarget; uniform float aspectRatio;',
    'uniform vec3 color; uniform vec2 point; uniform float radius;',
    'void main () {',
    '  vec2 p = vUv - point.xy; p.x *= aspectRatio;',
    '  vec3 splat = exp(-dot(p, p) / radius) * color;',
    '  gl_FragColor = vec4(texture2D(uTarget, vUv).xyz + splat, 1.0);',
    '}'].join('\n'));

  var advectionFS = compile(gl.FRAGMENT_SHADER, [
    'precision highp float; precision highp sampler2D;',
    'varying vec2 vUv; uniform sampler2D uVelocity; uniform sampler2D uSource;',
    'uniform vec2 texelSize; uniform vec2 dyeTexelSize; uniform float dt; uniform float dissipation;',
    'vec4 bilerp (sampler2D sam, vec2 uv, vec2 tsize) {',
    '  vec2 st = uv / tsize - 0.5; vec2 iuv = floor(st); vec2 fuv = fract(st);',
    '  vec4 a = texture2D(sam, (iuv + vec2(0.5, 0.5)) * tsize);',
    '  vec4 b = texture2D(sam, (iuv + vec2(1.5, 0.5)) * tsize);',
    '  vec4 c = texture2D(sam, (iuv + vec2(0.5, 1.5)) * tsize);',
    '  vec4 d = texture2D(sam, (iuv + vec2(1.5, 1.5)) * tsize);',
    '  return mix(mix(a, b, fuv.x), mix(c, d, fuv.x), fuv.y);',
    '}',
    'void main () {',
    '#ifdef MANUAL_FILTERING',
    '  vec2 coord = vUv - dt * bilerp(uVelocity, vUv, texelSize).xy * texelSize;',
    '  vec4 result = bilerp(uSource, coord, dyeTexelSize);',
    '#else',
    '  vec2 coord = vUv - dt * texture2D(uVelocity, vUv).xy * texelSize;',
    '  vec4 result = texture2D(uSource, coord);',
    '#endif',
    '  gl_FragColor = result / (1.0 + dissipation * dt);',
    '}'].join('\n'), ext.supportLinearFiltering ? null : ['MANUAL_FILTERING']);

  var divergenceFS = compile(gl.FRAGMENT_SHADER, [
    'precision mediump float; precision mediump sampler2D;',
    'varying highp vec2 vUv, vL, vR, vT, vB; uniform sampler2D uVelocity;',
    'void main () {',
    '  float L = texture2D(uVelocity, vL).x; float R = texture2D(uVelocity, vR).x;',
    '  float T = texture2D(uVelocity, vT).y; float B = texture2D(uVelocity, vB).y;',
    '  vec2 C = texture2D(uVelocity, vUv).xy;',
    '  if (vL.x < 0.0) { L = -C.x; } if (vR.x > 1.0) { R = -C.x; }',
    '  if (vT.y > 1.0) { T = -C.y; } if (vB.y < 0.0) { B = -C.y; }',
    '  gl_FragColor = vec4(0.5 * (R - L + T - B), 0.0, 0.0, 1.0);',
    '}'].join('\n'));

  var curlFS = compile(gl.FRAGMENT_SHADER, [
    'precision mediump float; precision mediump sampler2D;',
    'varying highp vec2 vUv, vL, vR, vT, vB; uniform sampler2D uVelocity;',
    'void main () {',
    '  float L = texture2D(uVelocity, vL).y; float R = texture2D(uVelocity, vR).y;',
    '  float T = texture2D(uVelocity, vT).x; float B = texture2D(uVelocity, vB).x;',
    '  gl_FragColor = vec4(0.5 * (R - L - T + B), 0.0, 0.0, 1.0);',
    '}'].join('\n'));

  var vorticityFS = compile(gl.FRAGMENT_SHADER, [
    'precision highp float; precision highp sampler2D;',
    'varying vec2 vUv, vL, vR, vT, vB; uniform sampler2D uVelocity; uniform sampler2D uCurl;',
    'uniform float curl; uniform float dt;',
    'void main () {',
    '  float L = texture2D(uCurl, vL).x; float R = texture2D(uCurl, vR).x;',
    '  float T = texture2D(uCurl, vT).x; float B = texture2D(uCurl, vB).x;',
    '  float C = texture2D(uCurl, vUv).x;',
    '  vec2 force = 0.5 * vec2(abs(T) - abs(B), abs(R) - abs(L));',
    '  force /= length(force) + 0.0001; force *= curl * C; force.y *= -1.0;',
    '  vec2 velocity = texture2D(uVelocity, vUv).xy + force * dt;',
    '  gl_FragColor = vec4(clamp(velocity, -1000.0, 1000.0), 0.0, 1.0);',
    '}'].join('\n'));

  var pressureFS = compile(gl.FRAGMENT_SHADER, [
    'precision mediump float; precision mediump sampler2D;',
    'varying highp vec2 vUv, vL, vR, vT, vB; uniform sampler2D uPressure; uniform sampler2D uDivergence;',
    'void main () {',
    '  float L = texture2D(uPressure, vL).x; float R = texture2D(uPressure, vR).x;',
    '  float T = texture2D(uPressure, vT).x; float B = texture2D(uPressure, vB).x;',
    '  float divergence = texture2D(uDivergence, vUv).x;',
    '  gl_FragColor = vec4((L + R + B + T - divergence) * 0.25, 0.0, 0.0, 1.0);',
    '}'].join('\n'));

  var gradientFS = compile(gl.FRAGMENT_SHADER, [
    'precision mediump float; precision mediump sampler2D;',
    'varying highp vec2 vUv, vL, vR, vT, vB; uniform sampler2D uPressure; uniform sampler2D uVelocity;',
    'void main () {',
    '  float L = texture2D(uPressure, vL).x; float R = texture2D(uPressure, vR).x;',
    '  float T = texture2D(uPressure, vT).x; float B = texture2D(uPressure, vB).x;',
    '  vec2 velocity = texture2D(uVelocity, vUv).xy - vec2(R - L, T - B);',
    '  gl_FragColor = vec4(velocity, 0.0, 1.0);',
    '}'].join('\n'));

  var copyProgram = new Program(baseVS, copyFS);
  var clearProgram = new Program(baseVS, clearFS);
  var displayProgram = new Program(baseVS, displayFS);
  var splatProgram = new Program(baseVS, splatFS);
  var advectionProgram = new Program(baseVS, advectionFS);
  var divergenceProgram = new Program(baseVS, divergenceFS);
  var curlProgram = new Program(baseVS, curlFS);
  var vorticityProgram = new Program(baseVS, vorticityFS);
  var pressureProgram = new Program(baseVS, pressureFS);
  var gradientProgram = new Program(baseVS, gradientFS);

  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, -1, 1, 1, 1, 1, -1]), gl.STATIC_DRAW);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array([0, 1, 2, 0, 2, 3]), gl.STATIC_DRAW);
  gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
  gl.enableVertexAttribArray(0);

  function blit(target, clear) {
    if (target == null) {
      gl.viewport(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight);
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    } else {
      gl.viewport(0, 0, target.width, target.height);
      gl.bindFramebuffer(gl.FRAMEBUFFER, target.fbo);
    }
    if (clear) { gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); }
    gl.drawElements(gl.TRIANGLES, 6, gl.UNSIGNED_SHORT, 0);
  }

  function createFBO(w, h, internalFormat, format, type, param) {
    gl.activeTexture(gl.TEXTURE0);
    var texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, param);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, param);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D, 0, internalFormat, w, h, 0, format, type, null);
    var fbo = gl.createFramebuffer();
    gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, texture, 0);
    gl.viewport(0, 0, w, h);
    gl.clear(gl.COLOR_BUFFER_BIT);
    return {
      texture: texture, fbo: fbo, width: w, height: h, texelSizeX: 1 / w, texelSizeY: 1 / h,
      attach: function (id) { gl.activeTexture(gl.TEXTURE0 + id); gl.bindTexture(gl.TEXTURE_2D, texture); return id; }
    };
  }

  function createDoubleFBO(w, h, internalFormat, format, type, param) {
    var a = createFBO(w, h, internalFormat, format, type, param);
    var b = createFBO(w, h, internalFormat, format, type, param);
    return {
      width: w, height: h, texelSizeX: a.texelSizeX, texelSizeY: a.texelSizeY,
      get read() { return a; }, set read(v) { a = v; },
      get write() { return b; }, set write(v) { b = v; },
      swap: function () { var t = a; a = b; b = t; }
    };
  }

  function resizeFBO(target, w, h, internalFormat, format, type, param) {
    var fresh = createFBO(w, h, internalFormat, format, type, param);
    copyProgram.bind();
    gl.uniform1i(copyProgram.uniforms.uTexture, target.attach(0));
    blit(fresh);
    return fresh;
  }

  function resizeDoubleFBO(target, w, h, internalFormat, format, type, param) {
    if (target.width === w && target.height === h) return target;
    target.read = resizeFBO(target.read, w, h, internalFormat, format, type, param);
    target.write = createFBO(w, h, internalFormat, format, type, param);
    target.width = w; target.height = h; target.texelSizeX = 1 / w; target.texelSizeY = 1 / h;
    return target;
  }

  function resolution(res) {
    var aspect = gl.drawingBufferWidth / gl.drawingBufferHeight;
    if (aspect < 1) aspect = 1 / aspect;
    var min = Math.round(res), max = Math.round(res * aspect);
    return gl.drawingBufferWidth > gl.drawingBufferHeight ? { width: max, height: min } : { width: min, height: max };
  }

  var dye, velocity, divergence, curl, pressure;
  function initFramebuffers() {
    var sim = resolution(config.SIM_RESOLUTION), dyeRes = resolution(config.DYE_RESOLUTION);
    var type = ext.halfFloatTexType, rgba = ext.formatRGBA, rg = ext.formatRG, r = ext.formatR;
    var filtering = ext.supportLinearFiltering ? gl.LINEAR : gl.NEAREST;
    gl.disable(gl.BLEND);
    dye = dye ? resizeDoubleFBO(dye, dyeRes.width, dyeRes.height, rgba.internalFormat, rgba.format, type, filtering)
              : createDoubleFBO(dyeRes.width, dyeRes.height, rgba.internalFormat, rgba.format, type, filtering);
    velocity = velocity ? resizeDoubleFBO(velocity, sim.width, sim.height, rg.internalFormat, rg.format, type, filtering)
                        : createDoubleFBO(sim.width, sim.height, rg.internalFormat, rg.format, type, filtering);
    divergence = createFBO(sim.width, sim.height, r.internalFormat, r.format, type, gl.NEAREST);
    curl = createFBO(sim.width, sim.height, r.internalFormat, r.format, type, gl.NEAREST);
    pressure = createDoubleFBO(sim.width, sim.height, r.internalFormat, r.format, type, gl.NEAREST);
  }

  function resizeCanvas() {
    var w = scaled(canvas.clientWidth), h = scaled(canvas.clientHeight);
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; return true; }
    return false;
  }

  function step(dt) {
    gl.disable(gl.BLEND);

    curlProgram.bind();
    gl.uniform2f(curlProgram.uniforms.texelSize, velocity.texelSizeX, velocity.texelSizeY);
    gl.uniform1i(curlProgram.uniforms.uVelocity, velocity.read.attach(0));
    blit(curl);

    vorticityProgram.bind();
    gl.uniform2f(vorticityProgram.uniforms.texelSize, velocity.texelSizeX, velocity.texelSizeY);
    gl.uniform1i(vorticityProgram.uniforms.uVelocity, velocity.read.attach(0));
    gl.uniform1i(vorticityProgram.uniforms.uCurl, curl.attach(1));
    gl.uniform1f(vorticityProgram.uniforms.curl, config.CURL);
    gl.uniform1f(vorticityProgram.uniforms.dt, dt);
    blit(velocity.write); velocity.swap();

    divergenceProgram.bind();
    gl.uniform2f(divergenceProgram.uniforms.texelSize, velocity.texelSizeX, velocity.texelSizeY);
    gl.uniform1i(divergenceProgram.uniforms.uVelocity, velocity.read.attach(0));
    blit(divergence);

    clearProgram.bind();
    gl.uniform1i(clearProgram.uniforms.uTexture, pressure.read.attach(0));
    gl.uniform1f(clearProgram.uniforms.value, config.PRESSURE);
    blit(pressure.write); pressure.swap();

    pressureProgram.bind();
    gl.uniform2f(pressureProgram.uniforms.texelSize, velocity.texelSizeX, velocity.texelSizeY);
    gl.uniform1i(pressureProgram.uniforms.uDivergence, divergence.attach(0));
    for (var i = 0; i < config.PRESSURE_ITERATIONS; i++) {
      gl.uniform1i(pressureProgram.uniforms.uPressure, pressure.read.attach(1));
      blit(pressure.write); pressure.swap();
    }

    gradientProgram.bind();
    gl.uniform2f(gradientProgram.uniforms.texelSize, velocity.texelSizeX, velocity.texelSizeY);
    gl.uniform1i(gradientProgram.uniforms.uPressure, pressure.read.attach(0));
    gl.uniform1i(gradientProgram.uniforms.uVelocity, velocity.read.attach(1));
    blit(velocity.write); velocity.swap();

    advectionProgram.bind();
    gl.uniform2f(advectionProgram.uniforms.texelSize, velocity.texelSizeX, velocity.texelSizeY);
    if (!ext.supportLinearFiltering) gl.uniform2f(advectionProgram.uniforms.dyeTexelSize, velocity.texelSizeX, velocity.texelSizeY);
    var vid = velocity.read.attach(0);
    gl.uniform1i(advectionProgram.uniforms.uVelocity, vid);
    gl.uniform1i(advectionProgram.uniforms.uSource, vid);
    gl.uniform1f(advectionProgram.uniforms.dt, dt);
    gl.uniform1f(advectionProgram.uniforms.dissipation, config.VELOCITY_DISSIPATION);
    blit(velocity.write); velocity.swap();

    if (!ext.supportLinearFiltering) gl.uniform2f(advectionProgram.uniforms.dyeTexelSize, dye.texelSizeX, dye.texelSizeY);
    gl.uniform1i(advectionProgram.uniforms.uVelocity, velocity.read.attach(0));
    gl.uniform1i(advectionProgram.uniforms.uSource, dye.read.attach(1));
    gl.uniform1f(advectionProgram.uniforms.dissipation, config.DENSITY_DISSIPATION);
    blit(dye.write); dye.swap();
  }

  function render() {
    gl.disable(gl.BLEND);
    displayProgram.bind();
    gl.uniform1f(displayProgram.uniforms.maxAlpha, config.MAX_ALPHA);
    gl.uniform1i(displayProgram.uniforms.uTexture, dye.read.attach(0));
    blit(null, true);
  }

  function splat(x, y, dx, dy, color, radiusScale) {
    var aspect = canvas.width / canvas.height;
    var radius = config.SPLAT_RADIUS / 100 * radiusScale;
    if (aspect > 1) radius *= aspect;
    splatProgram.bind();
    gl.uniform1i(splatProgram.uniforms.uTarget, velocity.read.attach(0));
    gl.uniform1f(splatProgram.uniforms.aspectRatio, aspect);
    gl.uniform2f(splatProgram.uniforms.point, x, y);
    gl.uniform3f(splatProgram.uniforms.color, dx, dy, 0);
    gl.uniform1f(splatProgram.uniforms.radius, radius);
    blit(velocity.write); velocity.swap();
    gl.uniform1i(splatProgram.uniforms.uTarget, dye.read.attach(0));
    gl.uniform3f(splatProgram.uniforms.color, color[0], color[1], color[2]);
    blit(dye.write); dye.swap();
  }

  // ---------- мышь ----------
  var pointer = { x: 0, y: 0, px: 0, py: 0, dx: 0, dy: 0, moved: false, ready: false };
  var hue = 0;            // 0 → #8FA4D1, 1 → #9377DF, плавно туда-обратно
  var lastMove = 0, running = false, lastTime = 0;

  window.addEventListener('mousemove', function (e) {
    var x = scaled(e.clientX) / canvas.width, y = 1 - scaled(e.clientY) / canvas.height;
    if (!pointer.ready) { pointer.x = x; pointer.y = y; pointer.ready = true; }
    pointer.px = pointer.x; pointer.py = pointer.y;
    pointer.x = x; pointer.y = y;
    var aspect = canvas.width / canvas.height;
    pointer.dx = (x - pointer.px) * (aspect < 1 ? aspect : 1);
    pointer.dy = (y - pointer.py) / (aspect > 1 ? aspect : 1);
    pointer.moved = pointer.dx !== 0 || pointer.dy !== 0;
    lastMove = performance.now();
    wake();
  }, { passive: true });

  function pointerColor(dt) {
    hue += dt * 0.35;
    var k = 0.5 - 0.5 * Math.cos(hue);                      // 0..1..0
    var speed = Math.min(Math.hypot(pointer.dx, pointer.dy) * 60, 1); // быстрее — ярче
    var strength = 0.25 + 0.5 * speed;
    return [
      (config.COLOR_A[0] + (config.COLOR_B[0] - config.COLOR_A[0]) * k) * strength,
      (config.COLOR_A[1] + (config.COLOR_B[1] - config.COLOR_A[1]) * k) * strength,
      (config.COLOR_A[2] + (config.COLOR_B[2] - config.COLOR_A[2]) * k) * strength
    ];
  }

  function frame(now) {
    if (!running) return;
    var dt = Math.min((now - lastTime) / 1000, 0.016666);
    lastTime = now;
    if (resizeCanvas()) initFramebuffers();
    if (pointer.moved) {
      pointer.moved = false;
      splat(pointer.x, pointer.y, pointer.dx * config.SPLAT_FORCE, pointer.dy * config.SPLAT_FORCE,
            pointerColor(dt), hover ? 1.3 : 1);
    }
    step(dt);
    render();
    // мышь стоит 1,5 с — след растаял, симуляцию ставим на паузу
    if (now - lastMove > 1500) { running = false; gl.clear(gl.COLOR_BUFFER_BIT); return; }
    requestAnimationFrame(frame);
  }

  function wake() {
    if (running || document.hidden) return;
    running = true;
    lastTime = performance.now();
    requestAnimationFrame(frame);
  }

  document.addEventListener('visibilitychange', function () {
    if (document.hidden) running = false;
  });

  resizeCanvas();
  initFramebuffers();
})();
