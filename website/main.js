const __CONNECTIA_LOGO_DATA_URI__ = 'data:image/png;base64,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tusBy/iYZDHg+wNHRqADANjeZZJZhnk+3O8pK3NfBnhv4EgJdAAAu/mS5DzJP9PPat1Vkh+TvOvhvYAT4xo6AID9naVskVwkebXj//2YcrOVms+5Axon0AEA9OMs5Rq785vfn9/798uU1b31nd8DHESgAwAAaJRr6AAAABol0AEAADRKoAMAAGiUQAcAANAogQ4AAKBRAh0AAECjBDoAAIBGCXQAAACNEugAAAAaJdABAAA0SqADAABolEAHAADQKIEOAACgUQIdAABAowQ6AACARgl0AAAAjRLoAAAAGiXQAQAANEqgAwAAaJRABwAA0CiBDgAAoFECHQAAQKMEOgAAgEYJdAAAAI0S6AAAABol0AEAADRKoAMAAGiUQAcAANAogQ4AAKBRAh0AAECjBDoAAIBGCXQAAACNEugAAAAaJdABAAA0SqADAABolEAHAADQKIEOAACgUQIdAABAowQ6AACARgl0AAAAjRLoAAAAGiXQAQAANEqgAwAAaJRABwAA0CiBDgAAoFECHQAAQKMEOgAAgEYJdAAAAI0S6AAAABol0AEAADRKoAMAAGiUQAcAANAogQ4AAKBRAh0AAECjBDoAAIBGCXQAAACNEugAAAAaJdABAAA0SqADAABolEAHAADQKIEOAACgUQIdAABAowQ6AACARgl0AAAAjRLoAAAAGiXQAQAANEqgAwAAaJRABwAA0CiBDgAAoFECHQAAQKMEOgAAgEYJdAAAAI0S6AAAABol0AEAADRKoAMAAGiUQAcAANAogQ4AAKBRAh0AAECjBDoAAIBGCXQAAACNEugAAAAaJdABAAA0SqADAABolEAHAADQKIEOAACgUQIdAABAowQ6AACARgl0AAAAjRLoAAAAGiXQAQAANEqgAwAAaJRABwAA0CiBDgAAoFECHQAAQKMEOgAAgEYJdAAAAI0S6AAAABol0AEAADRKoAMAAGiUQAcAANAogQ4AAKBRAh0AAECjBDoAAIBGCXQAAACNEugAAAAaJdABAAA0SqADAABolEAHAADQKIEOAACgUQIdAABAowQ6AACARgl0AAAAjRLoAAAAGiXQAQAANEqgAwAAaJRABwAA0CiBDgAAoFECHQAAQKMEOgAAgEb9tXYFAACAXpwlOU8yv/nz7OZ1meTLzd+t7/2Zxv3w9evX2nUAAAD2c5ZkcfN6tcP/u0ry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';

/* =========================================
   CONNECTIA — Main JS (Premium Cosmic v3)
   ========================================= */

// ============ I18N ============
const translations = {
  en: {
    loader_hello: "Hello, welcome to",
    menu: "Menu",
    lets_chat: "Let's chat",
    nav_home: "Home",
    nav_stack: "Specialties",
    nav_manifesto: "Manifesto",
    nav_work: "Work",
    nav_clients: "Clients",
    nav_contact: "Contact",
    get_in_touch: "Let's chat —",
    hero_tag: "Mexican creative brain · Urban culture",
    hero_we_are: "We are",
    scroll: "Scroll",
    ch_manifesto: "Manifesto · Creative brain",
    manifesto_l1: "We don't do",
    manifesto_l2: "Out of Home.",
    manifesto_l3: "We do",
    manifesto_l4: "Out of Noise.",
    brain_label: "Creative brain",
    brain_n1: "Intentional amplification · Landmarks · Cultural OOH",
    brain_n2: "Wow factor · Stands · Activations · Phygital",
    brain_n3: "Ideas that belong · Strategy · Narrative",
    brain_n4: "Brand content · UGC · Large-format printing",
    brain_hint: "Move the cursor to wake the brain",
    manifesto_sub: "Brands don't need to shout louder. They need to say something meaningful, in the right place, with the right voice, in front of the right community.",
    ch_stack: "Cultural Stack™",
    stack_t1: "Four specialties.",
    stack_t2: "One creative brain.",
    pillar1_tag: "Intentional amplification",
    pillar1_p: "We don't buy inventory: we <em>curate presence</em>. We're experts in <em>iconic landmarks</em> and signature placements that turn city spots into brand landmarks. Strategic OOH, contextual programmatic and cultural planning that places brands where the conversation is already happening.",
    pillar1_s1: "Iconic landmarks · signature placements",
    pillar1_s2: "Strategic OOH & curated street media",
    pillar1_s3: "Mass media planning & buying",
    pillar1_s4: "Contextual & behavioral programmatic",
    pillar1_s5: "Sponsorships & branded content",
    pillar1_s6: "Cultural impact measurement",
    pillar1_q: "The brand shows up where it matters, not where it's redundant.",
    pillar2_tag: "Wow factor in space",
    pillar2_p: "Space as interface. We design <em>activations with wow factor</em> that turn places into memorable moments. Installations, events, street performances, phygital experiences, stand fabrication, build-outs and sports sponsorships designed for participation, not observation.",
    pillar2_s1: "Wow-factor activations & street marketing",
    pillar2_s2: "Experiential events & launches",
    pillar2_s3: "Stand fabrication & build-outs",
    pillar2_s4: "Strategic sports sponsorships",
    pillar2_s5: "Fan experiences & venue activations",
    pillar2_s6: "Pop-ups, retail & phygital experiences",
    pillar2_q: "The city becomes the brand's stage.",
    pillar3_h: "Creative",
    pillar3_tag: "Ideas that belong",
    pillar3_p: "Concepts born <em>from culture</em>, not concepts trying to claim it. Creative direction, brand strategy and narratives designed to genuinely resonate with specific communities.",
    pillar3_s1: "Creative strategy & concepting",
    pillar3_s2: "Art direction & design",
    pillar3_s3: "Cultural & tonal copywriting",
    pillar3_s4: "Brand narrative & storytelling",
    pillar3_s5: "Visual & verbal identity",
    pillar3_s6: "Integrated campaigns",
    pillar3_q: "The brand speaks its audience's language.",
    pillar4_h: "Production",
    pillar4_tag: "Content that scales · UGC",
    pillar4_p: "Cinematic brand content, native social media formats and a specialty in <em>UGC engineering</em>: we don't just create content, we design the conditions for the audience to multiply it. Plus large-format printing and ad printing to take ideas from the digital archive to the street.",
    pillar4_s1: "UGC engineering & creator economy",
    pillar4_s2: "Brand content & high-end video",
    pillar4_s3: "Social media: native, always-on & trends",
    pillar4_s4: "Large-format & ad printing",
    pillar4_s5: "Photography & visual direction",
    pillar4_s6: "Post-production & motion graphics",
    pillar4_q: "The brand sparks conversation, not just messages.",
    stack_note: "Each specialty works alone, in combination, or as an integrated system. When they operate together, the brand stops imposing and starts adding to people's cultural experience.",
    ch_work: "Selected work",
    case1_p: "A curated mural in Roma Norte that turned a corner into an urban-culture mantra.",
    case2_p: "Neighborhood sports sponsorship turned into a UGC documentary series for social media.",
    case3_p: "Phygital activation in Monterrey with QRs hidden on walls: 1.4M organic impressions.",
    case4_p: "Culture-first OOH campaign with hyperlocal copy by neighborhood, read like editorial.",
    case5_p: "A pop-up in Mérida with local sound curation that became the season's must-go party.",
    case6_p: "A launch with no showroom: the city was the centerpiece. 8 cities, 1 narrative.",
    ch_clients: "They trust us",
    clientes_t1: "Brands that understand culture",
    clientes_t2: "isn't bought: it's built.",
    clientes_note: "Plus many other brands trusting their culture to Connectia.",
    ch_contact: "Let's talk",
    contact_l1: "Got an idea",
    contact_l2: "that deserves the street?",
    write_us: "Write us —",
    ftr_navigate: "Navigate",
    ftr_social: "Social",
    ftr_contact: "Contact",
    ftr_privacy: "Privacy",
    ftr_terms: "Terms",
  },
  es: {}
};

function applyLang(lang) {
  document.documentElement.setAttribute('data-lang', lang);
  document.documentElement.setAttribute('lang', lang === 'en' ? 'en' : 'es');
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (!el.dataset.es) el.dataset.es = el.innerHTML;
    if (lang === 'en' && translations.en[key]) {
      el.innerHTML = translations.en[key];
    } else {
      el.innerHTML = el.dataset.es;
    }
  });
  document.querySelectorAll('.lang-toggle__opt').forEach(opt => {
    opt.classList.toggle('is-active', opt.dataset.langSet === lang);
  });
}

/* ============ COSMIC CANVAS ============ */
class Cosmos {
  constructor(canvas, opts = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.opts = Object.assign({
      maxLinkDist: 160,
      cursorRadius: 220,
      starColor: 'rgba(110, 31, 161, 0.85)',
      starColor2: 'rgba(245, 243, 238, 0.7)',
      lineColor: '110, 31, 161',
      cursorColor: '138, 63, 196',
      density: 0.00006,
      drift: 0.18,
      twinkle: true,
      logo: null, // { src, widthRatio, revealRadius, decay }
    }, opts);
    this.stars = [];
    this.logoStars = [];
    this.logoLoaded = false;
    this.mouse = { x: -9999, y: -9999, active: false };
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (this.opts.logo) this.loadLogo();
    this.init();
  }
  loadLogo() {
    // Use the inlined base64 data URI (defined at top of file) — works under file:// without canvas taint
    const src = (typeof __CONNECTIA_LOGO_DATA_URI__ !== 'undefined' && __CONNECTIA_LOGO_DATA_URI__)
      ? __CONNECTIA_LOGO_DATA_URI__
      : this.opts.logo.src;
    const img = new Image();
    img.onload = () => {
      this.logoImg = img;
      this.logoLoaded = true;
      this.buildLogoStars();
    };
    img.onerror = (e) => console.warn('[Cosmos] Logo failed to load.', e);
    img.src = src;
  }
  buildLogoStars() {
    if (!this.logoLoaded || !this.w) return;
    const opts = this.opts.logo;
    const widthRatio = opts.widthRatio || 0.62;
    const targetW = Math.min(this.w * widthRatio, opts.maxWidth || 900);
    const aspect = this.logoImg.height / this.logoImg.width;
    const targetH = targetW * aspect;
    // High-resolution sampling for crisp letterforms (no pixelation)
    const scale = 3;
    const ow = Math.ceil(targetW * scale);
    const oh = Math.ceil(targetH * scale);
    const off = document.createElement('canvas');
    off.width = ow; off.height = oh;
    const c = off.getContext('2d');
    c.imageSmoothingEnabled = true;
    c.imageSmoothingQuality = 'high';
    c.drawImage(this.logoImg, 0, 0, ow, oh);
    let data;
    try {
      data = c.getImageData(0, 0, ow, oh).data;
    } catch (err) {
      console.warn('[Cosmos] Cannot read logo pixels (canvas tainted?). Logo constellation disabled.', err);
      return;
    }
    // Dense sampling — many tiny crisp points, sub-pixel positioning preserved via /scale
    const step = opts.step || 5;
    const points = [];
    for (let y = 0; y < oh; y += step) {
      for (let x = 0; x < ow; x += step) {
        const i = (y * ow + x) * 4;
        if (data[i + 3] > 160) points.push([x / scale, y / scale]);
      }
    }
    // Centered position so the logo is easy to discover
    const offsetX = (this.w - targetW) / 2;
    const offsetY = (this.h - targetH) / 2;
    // Tiny crisp points with sub-pixel jitter (avoids visible sampling grid) +
    // per-star oscillator data for the dissolve/reform effect
    this.logoStars = points.map(([x, y]) => ({
      tx: x + offsetX + (Math.random() - 0.5) * 1.6,
      ty: y + offsetY + (Math.random() - 0.5) * 1.6,
      r: 0.55 + Math.random() * 0.5,
      t: 0,
      seedX: Math.random() * Math.PI * 2,
      seedY: Math.random() * Math.PI * 2,
      speedX: 0.0006 + Math.random() * 0.0008,
      speedY: 0.0007 + Math.random() * 0.0008,
      driftAng: Math.random() * Math.PI * 2,
      driftDist: 6 + Math.random() * 18, // dispersion radius when fully dissolved
    }));
    console.log(`[Cosmos] Hidden logo: ${this.logoStars.length} stars seeded.`);
  }
  init() { this.resize(); this.bind(); this.loop(); }
  resize() {
    const r = this.canvas.getBoundingClientRect();
    this.w = r.width; this.h = r.height;
    this.canvas.width = this.w * this.dpr;
    this.canvas.height = this.h * this.dpr;
    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    this.spawn();
    if (this.logoLoaded) this.buildLogoStars();
  }
  spawn() {
    const count = Math.max(40, Math.min(180, Math.floor(this.w * this.h * this.opts.density)));
    this.stars = [];
    for (let i = 0; i < count; i++) {
      this.stars.push({
        x: Math.random() * this.w,
        y: Math.random() * this.h,
        vx: (Math.random() - 0.5) * this.opts.drift,
        vy: (Math.random() - 0.5) * this.opts.drift,
        r: Math.random() * 1.4 + 0.4,
        baseR: 0,
        twinkleSpeed: Math.random() * 0.02 + 0.005,
        twinklePhase: Math.random() * Math.PI * 2,
        purple: Math.random() < 0.35,
      });
    }
    this.stars.forEach(s => s.baseR = s.r);
  }
  bind() {
    let t;
    window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(() => this.resize(), 150); });
    window.addEventListener('mousemove', (e) => {
      const r = this.canvas.getBoundingClientRect();
      this.mouse.x = e.clientX - r.left;
      this.mouse.y = e.clientY - r.top;
      this.mouse.active = (this.mouse.x >= 0 && this.mouse.x <= this.w && this.mouse.y >= 0 && this.mouse.y <= this.h);
    });
    window.addEventListener('mouseleave', () => { this.mouse.active = false; });

    // Touch support for mobile/tablet
    const handleTouch = (e) => {
      const touch = e.touches[0];
      if (!touch) return;
      const r = this.canvas.getBoundingClientRect();
      this.mouse.x = touch.clientX - r.left;
      this.mouse.y = touch.clientY - r.top;
      this.mouse.active = (this.mouse.x >= 0 && this.mouse.x <= this.w && this.mouse.y >= 0 && this.mouse.y <= this.h);
    };
    window.addEventListener('touchstart', handleTouch, { passive: true });
    window.addEventListener('touchmove', handleTouch, { passive: true });
    window.addEventListener('touchend', () => { this.mouse.active = false; });

    // Direct touch listeners on canvas for mobile (canvas has pointer-events:none in CSS)
    this.canvas.addEventListener('touchstart', (e) => {
      const touch = e.touches[0];
      if (!touch) return;
      const r = this.canvas.getBoundingClientRect();
      this.mouse.x = touch.clientX - r.left;
      this.mouse.y = touch.clientY - r.top;
      this.mouse.active = true;
    }, { passive: true });
    this.canvas.addEventListener('touchmove', (e) => {
      const touch = e.touches[0];
      if (!touch) return;
      const r = this.canvas.getBoundingClientRect();
      this.mouse.x = touch.clientX - r.left;
      this.mouse.y = touch.clientY - r.top;
      this.mouse.active = true;
    }, { passive: true });
    this.canvas.addEventListener('touchend', () => { this.mouse.active = false; });
  }
  loop() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.w, this.h);
    for (let s of this.stars) {
      s.x += s.vx; s.y += s.vy;
      if (s.x < -10) s.x = this.w + 10;
      if (s.x > this.w + 10) s.x = -10;
      if (s.y < -10) s.y = this.h + 10;
      if (s.y > this.h + 10) s.y = -10;
      if (this.opts.twinkle) {
        s.twinklePhase += s.twinkleSpeed;
        s.r = s.baseR * (0.7 + 0.6 * Math.abs(Math.sin(s.twinklePhase)));
      }
    }
    const max = this.opts.maxLinkDist;
    for (let i = 0; i < this.stars.length; i++) {
      for (let j = i + 1; j < this.stars.length; j++) {
        const a = this.stars[i], b = this.stars[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const d2 = dx * dx + dy * dy;
        if (d2 < max * max) {
          const t = 1 - Math.sqrt(d2) / max;
          ctx.strokeStyle = `rgba(${this.opts.lineColor}, ${t * 0.18})`;
          ctx.lineWidth = 0.6;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    }
    if (this.mouse.active) {
      const cr = this.opts.cursorRadius;
      for (let s of this.stars) {
        const dx = s.x - this.mouse.x, dy = s.y - this.mouse.y;
        const d2 = dx * dx + dy * dy;
        if (d2 < cr * cr) {
          const t = 1 - Math.sqrt(d2) / cr;
          ctx.strokeStyle = `rgba(${this.opts.cursorColor}, ${t * 0.7})`;
          ctx.lineWidth = 0.8;
          ctx.beginPath();
          ctx.moveTo(s.x, s.y); ctx.lineTo(this.mouse.x, this.mouse.y);
          ctx.stroke();
        }
      }
      const grad = ctx.createRadialGradient(this.mouse.x, this.mouse.y, 0, this.mouse.x, this.mouse.y, 60);
      grad.addColorStop(0, `rgba(${this.opts.cursorColor}, 0.18)`);
      grad.addColorStop(1, `rgba(${this.opts.cursorColor}, 0)`);
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(this.mouse.x, this.mouse.y, 60, 0, Math.PI * 2);
      ctx.fill();
    }
    for (let s of this.stars) {
      ctx.fillStyle = s.purple ? this.opts.starColor : this.opts.starColor2;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();
      if (s.purple && s.r > 1) {
        ctx.fillStyle = `rgba(${this.opts.lineColor}, 0.15)`;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r * 3, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // ===== HIDDEN LOGO CONSTELLATION (dissolve / reform) =====
    if (this.logoStars.length) {
      const opts = this.opts.logo || {};
      const revealR = opts.revealRadius || 180;
      const decay = opts.decay || 0.018;
      const nowMs = performance.now();

      // Activate stars within cursor radius (cursor proximity to TARGET position, not drifted position)
      if (this.mouse.active) {
        const r2 = revealR * revealR;
        for (let i = 0; i < this.logoStars.length; i++) {
          const ls = this.logoStars[i];
          const dx = ls.tx - this.mouse.x;
          const dy = ls.ty - this.mouse.y;
          const d2 = dx * dx + dy * dy;
          if (d2 < r2) {
            const intensity = 1 - Math.sqrt(d2) / revealR;
            ls.t = Math.max(ls.t, intensity);
          }
        }
      }

      // Pure white logo dots, two passes (halo + core)
      // Each star drifts away from its target proportional to (1 - t):
      //   t = 1 → exact position (logo formed)
      //   t = 0 → drifted by driftDist * sin/cos oscillation (dissolved)
      ctx.fillStyle = 'rgba(255, 255, 255, 1)';

      // Pass 1: halo
      for (let i = 0; i < this.logoStars.length; i++) {
        const ls = this.logoStars[i];
        if (ls.t > 0.02) {
          const dispersion = (1 - ls.t) * (1 - ls.t); // ease-in: most movement at low t
          const ox = Math.sin(nowMs * ls.speedX + ls.seedX) * ls.driftDist * dispersion;
          const oy = Math.cos(nowMs * ls.speedY + ls.seedY) * ls.driftDist * dispersion;
          ctx.globalAlpha = ls.t * 0.18;
          ctx.beginPath();
          ctx.arc(ls.tx + ox, ls.ty + oy, ls.r + 1.4, 0, Math.PI * 2);
          ctx.fill();
        }
      }
      // Pass 2: sharp core only for activated stars (logo invisible until cursor reveals)
      for (let i = 0; i < this.logoStars.length; i++) {
        const ls = this.logoStars[i];
        if (ls.t > 0.02) {
          const dispersion = (1 - ls.t) * (1 - ls.t);
          const ox = Math.sin(nowMs * ls.speedX + ls.seedX) * ls.driftDist * dispersion;
          const oy = Math.cos(nowMs * ls.speedY + ls.seedY) * ls.driftDist * dispersion;
          ctx.globalAlpha = ls.t;
          ctx.beginPath();
          ctx.arc(ls.tx + ox, ls.ty + oy, ls.r, 0, Math.PI * 2);
          ctx.fill();
          ls.t = Math.max(0, ls.t - decay);
        }
      }
      ctx.globalAlpha = 1;
    }

    requestAnimationFrame(() => this.loop());
  }
}

/* ============ BIG BANG (kept for future use; not initialized) ============ */
class BigBang {
  constructor(canvas, flashEl, onDone) {
    this.canvas = canvas;
    this.flashEl = flashEl;
    this.ctx = canvas.getContext('2d');
    this.onDone = onDone || (() => {});
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.particles = [];
    this.phase = 'idle';
    this.phaseT = 0;
    this.lastFrame = 0;
    this.logoLoaded = false;
    this.logoImg = new Image();
    this.logoImg.onload = () => { this.logoLoaded = true; };
    this.logoImg.src = '../assets/logo-white.svg';
    this.resize();
  }
  resize() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.w = w; this.h = h;
    this.canvas.width = w * this.dpr; this.canvas.height = h * this.dpr;
    this.canvas.style.width = w + 'px'; this.canvas.style.height = h + 'px';
    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
  }
  // Sample particle target positions from the actual loader logo position+size
  buildLogoTargets(logoEl) {
    let centerX = this.w / 2, centerY = this.h / 2;
    let targetW = 320, targetH = 70;
    if (logoEl) {
      const r = logoEl.getBoundingClientRect();
      if (r.width > 0) {
        targetW = r.width;
        targetH = r.height;
        centerX = r.left + r.width / 2;
        centerY = r.top + r.height / 2;
      }
    }
    // Render at 2x for sharper pixel sampling
    const scale = 2;
    const ow = Math.ceil(targetW * scale);
    const oh = Math.ceil(targetH * scale);
    const off = document.createElement('canvas');
    off.width = ow; off.height = oh;
    const c = off.getContext('2d');

    if (this.logoLoaded) {
      // Use the actual SVG logo for accurate pixel shape (incl. dot cluster)
      c.drawImage(this.logoImg, 0, 0, ow, oh);
    } else {
      // Fallback: render text "connectia"
      c.fillStyle = '#fff';
      c.textBaseline = 'middle';
      c.textAlign = 'center';
      let fs = oh * 0.78;
      c.font = `800 ${fs}px "Inter Tight", system-ui, sans-serif`;
      c.fillText('connectia', ow / 2, oh / 2);
    }
    const data = c.getImageData(0, 0, ow, oh).data;
    const points = [];
    const step = Math.max(2, Math.floor(Math.sqrt((ow * oh) / 7000)));
    for (let y = 0; y < oh; y += step) {
      for (let x = 0; x < ow; x += step) {
        const i = (y * ow + x) * 4;
        if (data[i + 3] > 128) points.push([x / scale, y / scale]);
      }
    }
    const offsetX = centerX - targetW / 2;
    const offsetY = centerY - targetH / 2;
    return points.map(([x, y]) => [x + offsetX, y + offsetY]);
  }
  spawn(logoEl) {
    const targets = this.buildLogoTargets(logoEl);
    const cx = this.w / 2, cy = this.h / 2;
    // Particles START at logo positions (logo intact)
    this.particles = targets.map((t) => ({
      x: t[0], y: t[1],
      vx: 0, vy: 0,
      tx: t[0], ty: t[1],
      dx: 0, dy: 0,
      size: 0.9 + Math.random() * 1.4,
      purple: Math.random() < 0.18, // mostly white (logo color), few purple sparkles
      bright: Math.random() < 0.12,
      seed: Math.random() * Math.PI * 2,
    }));
    // Pre-compute dispersal targets (used during disperse phase)
    for (const p of this.particles) {
      const a = Math.atan2(p.ty - cy, p.tx - cx) + (Math.random() - 0.5) * 0.6;
      const r = Math.max(this.w, this.h) * 0.7 + Math.random() * 200;
      p.dx = cx + Math.cos(a) * r;
      p.dy = cy + Math.sin(a) * r;
    }
  }
  start(logoEl) {
    this.spawn(logoEl);
    this.logoEl = logoEl;
    this.canvas.classList.add('is-active');
    this.phase = 'logo'; this.phaseT = 0;
    this.lastFrame = performance.now();
    requestAnimationFrame((t) => this.loop(t));
  }
  setPhase(name) { this.phase = name; this.phaseT = 0; }
  loop(now) {
    const dt = Math.min(40, now - this.lastFrame) / 1000;
    this.lastFrame = now;
    this.phaseT += dt;
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.w, this.h);

    if (this.phase === 'logo') {
      // Particles AT logo positions, gentle breathing — looks like the logo
      for (const p of this.particles) {
        p.x = p.tx + Math.sin(now * 0.0015 + p.seed) * 0.6;
        p.y = p.ty + Math.cos(now * 0.0018 + p.seed) * 0.6;
      }
      // Cross-fade: particles ramp up while logo image fades out
      if (this.phaseT > 0.15 && this.logoEl && !this.logoEl.classList.contains('is-fading')) {
        this.logoEl.classList.add('is-fading');
      }
      if (this.phaseT > 0.6) this.setPhase('dissolve');
    }
    else if (this.phase === 'dissolve') {
      // Logo disintegrates — jitter grows, particles drift outward slightly
      const t = Math.min(1, this.phaseT / 0.7);
      const amp = 1 + t * t * 8; // accelerating jitter 1px → 9px
      for (const p of this.particles) {
        p.x = p.tx + (Math.random() - 0.5) * amp + Math.sin(now * 0.003 + p.seed) * (1 + t * 2);
        p.y = p.ty + (Math.random() - 0.5) * amp + Math.cos(now * 0.003 + p.seed) * (1 + t * 2);
      }
      if (this.phaseT > 0.7) {
        // BANG: trigger flash and assign explosion velocities radiating outward
        const cx = this.w / 2, cy = this.h / 2;
        for (const p of this.particles) {
          const angle = Math.atan2(p.ty - cy, p.tx - cx) + (Math.random() - 0.5) * 0.5;
          const speed = 9 + Math.random() * 22;
          p.vx = Math.cos(angle) * speed;
          p.vy = Math.sin(angle) * speed;
        }
        this.flashEl.classList.add('is-flash');
        this.setPhase('bang');
      }
    }
    else if (this.phase === 'bang') {
      // Explosive expansion outward
      for (const p of this.particles) {
        p.x += p.vx;
        p.y += p.vy;
        p.vx *= 0.94;
        p.vy *= 0.94;
      }
      if (this.phaseT > 0.7) this.setPhase('disperse');
    }
    else if (this.phase === 'disperse') {
      const t = Math.min(1, this.phaseT / 1.4);
      const ease = t * t;
      for (const p of this.particles) {
        p.x += (p.dx - p.x) * (0.02 + ease * 0.04);
        p.y += (p.dy - p.y) * (0.02 + ease * 0.04);
      }
      if (this.phaseT > 0.3 && !this.canvas.classList.contains('is-fading')) {
        this.canvas.classList.add('is-fading');
        document.body.classList.add('is-revealed');
      }
      if (this.phaseT > 1.5) {
        this.phase = 'done';
        this.canvas.style.display = 'none';
        this.onDone();
        return;
      }
    }

    // Draw particles
    for (const p of this.particles) {
      const r = p.size + (p.bright ? 0.8 : 0);
      ctx.fillStyle = p.purple
        ? `rgba(168, 90, 222, ${p.bright ? 1 : 0.85})`
        : `rgba(245, 243, 238, ${p.bright ? 1 : 0.92})`;
      ctx.beginPath();
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
      ctx.fill();
      if (p.bright) {
        ctx.fillStyle = p.purple ? 'rgba(138, 63, 196, 0.25)' : 'rgba(245, 243, 238, 0.22)';
        ctx.beginPath();
        ctx.arc(p.x, p.y, r * 4, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Trails on bang/disperse
    if (this.phase === 'bang' || this.phase === 'disperse') {
      ctx.strokeStyle = 'rgba(168, 90, 222, 0.18)';
      ctx.lineWidth = 0.6;
      for (const p of this.particles) {
        if (Math.abs(p.vx) + Math.abs(p.vy) > 0.5) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y); ctx.lineTo(p.x - p.vx * 2, p.y - p.vy * 2);
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame((t) => this.loop(t));
  }
}

/* ============ BRAIN — interactive central scene ============ */
class Brain {
  constructor(container, canvas, coreEl, nodes) {
    this.container = container;
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.coreEl = coreEl;
    this.nodes = nodes;
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.stars = [];
    this.mouse = { x: -9999, y: -9999, active: false };
    this.activeNode = null;
    this.resize();
    this.bind();
    this.loop();
  }
  resize() {
    const r = this.canvas.getBoundingClientRect();
    this.w = r.width; this.h = r.height;
    this.canvas.width = this.w * this.dpr; this.canvas.height = this.h * this.dpr;
    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    this.spawn();
    this.measureNodes();
  }
  spawn() {
    const count = Math.floor(this.w * this.h * 0.0001);
    this.stars = [];
    for (let i = 0; i < count; i++) {
      this.stars.push({
        x: Math.random() * this.w,
        y: Math.random() * this.h,
        vx: (Math.random() - 0.5) * 0.15,
        vy: (Math.random() - 0.5) * 0.15,
        r: Math.random() * 1.2 + 0.3,
        baseR: 0,
        twinklePhase: Math.random() * Math.PI * 2,
        twinkleSpeed: Math.random() * 0.02 + 0.005,
        purple: Math.random() < 0.4,
      });
    }
    this.stars.forEach(s => s.baseR = s.r);
  }
  measureNodes() {
    const cr = this.container.getBoundingClientRect();
    this.center = { x: this.w / 2, y: this.h / 2 };
    this.nodePositions = this.nodes.map(n => {
      const r = n.getBoundingClientRect();
      return {
        el: n,
        x: r.left + r.width / 2 - cr.left,
        y: r.top + r.height / 2 - cr.top,
        w: r.width, h: r.height,
      };
    });
  }
  bind() {
    let t;
    window.addEventListener('resize', () => {
      clearTimeout(t); t = setTimeout(() => this.resize(), 150);
    });
    this.container.addEventListener('mousemove', (e) => {
      const r = this.canvas.getBoundingClientRect();
      this.mouse.x = e.clientX - r.left;
      this.mouse.y = e.clientY - r.top;
      this.mouse.active = true;

      // Activate core if cursor is near center
      const dxc = this.mouse.x - this.center.x;
      const dyc = this.mouse.y - this.center.y;
      const dCore = Math.sqrt(dxc * dxc + dyc * dyc);
      if (dCore < 180) this.coreEl.classList.add('is-active');
      else this.coreEl.classList.remove('is-active');

      // Activate closest node within range
      let closest = null, mind = Infinity;
      for (const n of this.nodePositions) {
        const dx = this.mouse.x - n.x, dy = this.mouse.y - n.y;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < mind) { mind = d; closest = n; }
      }
      if (closest && mind < 180) {
        if (this.activeNode !== closest.el) {
          this.nodePositions.forEach(p => p.el.classList.remove('is-active'));
          closest.el.classList.add('is-active');
          this.activeNode = closest.el;
        }
      } else if (this.activeNode) {
        this.activeNode.classList.remove('is-active');
        this.activeNode = null;
      }
    });
    this.container.addEventListener('mouseleave', () => {
      this.mouse.active = false;
      if (this.activeNode) { this.activeNode.classList.remove('is-active'); this.activeNode = null; }
      this.coreEl.classList.remove('is-active');
    });
  }
  loop() {
    const ctx = this.ctx;
    const now = performance.now();
    ctx.clearRect(0, 0, this.w, this.h);

    // Cosmic dust BLOBS at logo + node positions (always visible — looks like part of universe)
    if (this.center) {
      const blobs = [
        { x: this.center.x, y: this.center.y, r: 130, alpha: 0.32 },
      ];
      if (this.nodePositions) {
        for (const n of this.nodePositions) {
          blobs.push({ x: n.x, y: n.y, r: 80, alpha: 0.22 });
        }
      }
      for (const b of blobs) {
        const grad = ctx.createRadialGradient(b.x, b.y, 0, b.x, b.y, b.r);
        grad.addColorStop(0, `rgba(168, 90, 222, ${b.alpha})`);
        grad.addColorStop(0.5, `rgba(110, 31, 161, ${b.alpha * 0.4})`);
        grad.addColorStop(1, 'rgba(110, 31, 161, 0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Update stars
    for (let s of this.stars) {
      s.x += s.vx; s.y += s.vy;
      if (s.x < -10) s.x = this.w + 10; if (s.x > this.w + 10) s.x = -10;
      if (s.y < -10) s.y = this.h + 10; if (s.y > this.h + 10) s.y = -10;
      s.twinklePhase += s.twinkleSpeed;
      s.r = s.baseR * (0.6 + 0.7 * Math.abs(Math.sin(s.twinklePhase)));
    }

    // Draw constellation lines between stars
    for (let i = 0; i < this.stars.length; i++) {
      for (let j = i + 1; j < this.stars.length; j++) {
        const a = this.stars[i], b = this.stars[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const d2 = dx * dx + dy * dy;
        if (d2 < 18000) {
          const t = 1 - Math.sqrt(d2) / 134;
          ctx.strokeStyle = `rgba(168, 90, 222, ${t * 0.16})`;
          ctx.lineWidth = 0.5;
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
        }
      }
    }

    // Draw lines from center to each node (always visible, faintly)
    if (this.nodePositions) {
      for (const n of this.nodePositions) {
        const isActive = n.el === this.activeNode;
        const base = isActive ? 0.85 : 0.18;
        const grad = ctx.createLinearGradient(this.center.x, this.center.y, n.x, n.y);
        grad.addColorStop(0, `rgba(168, 90, 222, ${base})`);
        grad.addColorStop(1, `rgba(245, 243, 238, ${base * 0.6})`);
        ctx.strokeStyle = grad;
        ctx.lineWidth = isActive ? 1.6 : 0.7;
        ctx.beginPath();
        ctx.moveTo(this.center.x, this.center.y);
        ctx.lineTo(n.x, n.y);
        ctx.stroke();

        // pulse dot traveling along the active line
        if (isActive) {
          const t = (now * 0.0012) % 1;
          const px = this.center.x + (n.x - this.center.x) * t;
          const py = this.center.y + (n.y - this.center.y) * t;
          ctx.fillStyle = 'rgba(245, 243, 238, 0.95)';
          ctx.beginPath(); ctx.arc(px, py, 3, 0, Math.PI * 2); ctx.fill();
          ctx.fillStyle = 'rgba(168, 90, 222, 0.4)';
          ctx.beginPath(); ctx.arc(px, py, 8, 0, Math.PI * 2); ctx.fill();
        }
      }
    }

    // Cursor → nearby stars connections
    if (this.mouse.active) {
      const cr = 220;
      for (let s of this.stars) {
        const dx = s.x - this.mouse.x, dy = s.y - this.mouse.y;
        const d2 = dx * dx + dy * dy;
        if (d2 < cr * cr) {
          const t = 1 - Math.sqrt(d2) / cr;
          ctx.strokeStyle = `rgba(245, 243, 238, ${t * 0.7})`;
          ctx.lineWidth = 0.8;
          ctx.beginPath();
          ctx.moveTo(s.x, s.y); ctx.lineTo(this.mouse.x, this.mouse.y);
          ctx.stroke();
        }
      }
      // Cursor → center connection
      const dx = this.center.x - this.mouse.x, dy = this.center.y - this.mouse.y;
      const d = Math.sqrt(dx * dx + dy * dy);
      if (d < 350) {
        const t = 1 - d / 350;
        ctx.strokeStyle = `rgba(168, 90, 222, ${t * 0.6})`;
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(this.mouse.x, this.mouse.y); ctx.lineTo(this.center.x, this.center.y);
        ctx.stroke();
      }
    }

    // Draw stars
    for (let s of this.stars) {
      ctx.fillStyle = s.purple ? 'rgba(168, 90, 222, 0.9)' : 'rgba(245, 243, 238, 0.85)';
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(() => this.loop());
  }
}

/* ============ LOGO SPOTLIGHT — cursor reveals cosmic universe inside the giant logo ============ */
function setupLogoSpotlight(container) {
  if (!container) return;
  const stack = container.querySelector('.logo-stack');
  if (!stack) return;
  const hero = container.closest('.hero') || document.body;
  // Cursor anywhere in hero: spotlight follows. Cursor leaves hero: logo fades out and mask resets off-screen.
  hero.addEventListener('mousemove', (e) => {
    const r = stack.getBoundingClientRect();
    const x = e.clientX - r.left;
    const y = e.clientY - r.top;
    stack.style.setProperty('--mx', x + 'px');
    stack.style.setProperty('--my', y + 'px');
    container.classList.add('is-active');
  });
  hero.addEventListener('mouseleave', () => {
    container.classList.remove('is-active');
    // Reset mask off-screen so the logo is fully invisible
    setTimeout(() => {
      stack.style.setProperty('--mx', '-9999px');
      stack.style.setProperty('--my', '-9999px');
    }, 700);
  });
}

/* ============ COSMIC LETTERS — cursor proximity light-up (legacy, unused) ============ */
function setupCosmicLetters(wordmarkEl, radius = 140) {
  if (!wordmarkEl) return;
  const cells = Array.from(wordmarkEl.querySelectorAll('.cell'));
  if (!cells.length) return;
  let centers = [];
  const recompute = () => {
    centers = cells.map(c => {
      const r = c.getBoundingClientRect();
      return { el: c, x: r.left + r.width / 2, y: r.top + r.height / 2 };
    });
  };
  recompute();
  let resizeT;
  window.addEventListener('resize', () => { clearTimeout(resizeT); resizeT = setTimeout(recompute, 120); });
  window.addEventListener('scroll', () => { clearTimeout(resizeT); resizeT = setTimeout(recompute, 80); }, { passive: true });

  window.addEventListener('mousemove', (e) => {
    for (const c of centers) {
      const dx = c.x - e.clientX;
      const dy = c.y - e.clientY;
      const d = Math.sqrt(dx * dx + dy * dy);
      if (d < radius) c.el.classList.add('is-lit');
      else c.el.classList.remove('is-lit');
    }
  });
}

/* ============ MAGNETIC BUTTONS ============ */
function setupMagnetic() {
  document.querySelectorAll('[data-magnetic]').forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
      const r = btn.getBoundingClientRect();
      const cx = r.left + r.width / 2;
      const cy = r.top + r.height / 2;
      const dx = (e.clientX - cx) * 0.25;
      const dy = (e.clientY - cy) * 0.25;
      btn.style.transform = `translate(${dx}px, ${dy}px)`;
    });
    btn.addEventListener('mouseleave', () => { btn.style.transform = ''; });
  });
}

/* ============ CLIENT CARDS — spotlight ============ */
function setupClientSpotlight() {
  document.querySelectorAll('.client-cell').forEach(cell => {
    cell.addEventListener('mousemove', (e) => {
      const r = cell.getBoundingClientRect();
      cell.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100) + '%');
      cell.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100) + '%');
    });
  });
}

/* ============ PARTICLE TEXT — comets/dust converge into text on hover ============ */
class ParticleText {
  constructor(el) {
    this.el = el;
    this.text = el.dataset.text || el.textContent.trim();
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'particle-text-canvas';
    this.canvas.setAttribute('aria-hidden', 'true');
    el.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.particles = [];
    this.formAmt = 0;
    this.isHovered = false;
    this.padX = 220;  // wide canvas: particles fly far without forming the word
    this.padY = 110;

    this.resize();
    let resizeT;
    window.addEventListener('resize', () => { clearTimeout(resizeT); resizeT = setTimeout(() => this.resize(), 200); });

    this.el.addEventListener('mouseenter', () => { this.isHovered = true; });
    this.el.addEventListener('mouseleave', () => { this.isHovered = false; });

    requestAnimationFrame((t) => this.loop(t));
  }
  resize() {
    const rect = this.el.getBoundingClientRect();
    if (rect.width < 10) {
      setTimeout(() => this.resize(), 250);
      return;
    }
    this.tw = rect.width;
    this.th = rect.height;
    this.cw = this.tw + this.padX * 2;
    this.ch = this.th + this.padY * 2;
    this.canvas.width = this.cw * this.dpr;
    this.canvas.height = this.ch * this.dpr;
    this.canvas.style.width = this.cw + 'px';
    this.canvas.style.height = this.ch + 'px';
    this.canvas.style.left = -this.padX + 'px';
    this.canvas.style.top = -this.padY + 'px';
    this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);

    // Sample text pixel positions using same font as the source element
    const off = document.createElement('canvas');
    off.width = this.tw;
    off.height = this.th;
    const c = off.getContext('2d');
    const cs = window.getComputedStyle(this.el);
    c.fillStyle = '#fff';
    const font = `${cs.fontStyle || 'italic'} ${cs.fontWeight || 400} ${cs.fontSize} ${cs.fontFamily || 'serif'}`;
    c.font = font;
    c.textBaseline = 'middle';
    c.textAlign = 'left';
    c.fillText(this.text, 0, this.th / 2);

    const data = c.getImageData(0, 0, this.tw, this.th).data;
    const targets = [];
    const step = 5;
    for (let y = 0; y < this.th; y += step) {
      for (let x = 0; x < this.tw; x += step) {
        const i = (y * this.tw + x) * 4;
        if (data[i + 3] > 130) targets.push([x + this.padX, y + this.padY]);
      }
    }

    // Build particles with TOTALLY chaotic rest positions — flying free across the canvas
    this.particles = targets.map(t => {
      const rx = Math.random() * this.cw;
      const ry = Math.random() * this.ch;
      return {
        tx: t[0], ty: t[1],
        rx, ry,
        x: rx, y: ry,
        vx: (Math.random() - 0.5) * 1.4,
        vy: (Math.random() - 0.5) * 1.0,
        seed: Math.random() * Math.PI * 2,
        seed2: Math.random() * Math.PI * 2,
        size: 0.6 + Math.random() * 1.0,
        bright: Math.random() < 0.10,
      };
    });
  }
  loop(now) {
    const ctx = this.ctx;
    if (!this.particles.length) {
      requestAnimationFrame((t) => this.loop(t));
      return;
    }
    // Trail effect: fade old positions instead of full clear
    ctx.fillStyle = 'rgba(5, 2, 17, 0.32)';
    ctx.fillRect(0, 0, this.cw, this.ch);

    const target = this.isHovered ? 1 : 0;
    this.formAmt += (target - this.formAmt) * 0.07;

    const formStrong = this.formAmt > 0.92;
    for (const p of this.particles) {
      if (formStrong) {
        // Locked into text shape with subtle breathing
        p.x = p.tx + Math.sin(now * 0.001 + p.seed) * 0.6;
        p.y = p.ty + Math.cos(now * 0.0012 + p.seed) * 0.6;
      } else {
        // FREE FLIGHT: no aggregation around text — particles roam the whole canvas
        if (Math.random() < 0.04) {
          p.vx += (Math.random() - 0.5) * 0.35;
          p.vy += (Math.random() - 0.5) * 0.28;
        }
        // Curl-noise-like organic drift with two oscillators
        p.vx += Math.sin(now * 0.0008 + p.seed) * 0.04;
        p.vy += Math.cos(now * 0.0011 + p.seed2) * 0.04;
        p.vx *= 0.97; p.vy *= 0.97;
        // Bounce off canvas edges so dust stays in bounds without aggregating
        if (p.x < 0) p.vx = Math.abs(p.vx);
        if (p.x > this.cw) p.vx = -Math.abs(p.vx);
        if (p.y < 0) p.vy = Math.abs(p.vy);
        if (p.y > this.ch) p.vy = -Math.abs(p.vy);
        // Form pull only kicks in significantly when hovered
        const formX = (p.tx - p.x) * 0.09 * this.formAmt;
        const formY = (p.ty - p.y) * 0.09 * this.formAmt;
        p.x += p.vx * (1 - this.formAmt * 0.8) + formX;
        p.y += p.vy * (1 - this.formAmt * 0.8) + formY;
      }
      // Render — grey dust with occasional bright sparkle
      const v = 130 + Math.random() * 95;
      const alpha = p.bright ? 1 : (0.65 + this.formAmt * 0.35);
      ctx.fillStyle = p.bright
        ? `rgba(245, 243, 238, ${alpha})`
        : `rgba(${v}, ${v}, ${v}, ${alpha})`;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size + (p.bright ? 0.5 : 0), 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame((t) => this.loop(t));
  }
}

/* ============ MAIN ============ */
document.addEventListener('DOMContentLoaded', () => {
  // Cosmic canvases — interactive universe across every section
  // Dark sections (Hero, Manifesto, Contact, Footer): bright stars
  const darkCosmosOpts = {
    starColor: 'rgba(168, 90, 222, 0.95)',
    starColor2: 'rgba(245, 243, 238, 0.85)',
    lineColor: '138, 63, 196',
    cursorColor: '245, 243, 238',
    maxLinkDist: 180,
    cursorRadius: 260,
    density: 0.0001,
  };
  // Paper sections (Stack, Work, Clientes): dark stars (multiply blend in CSS)
  const paperCosmosOpts = {
    starColor: 'rgba(110, 31, 161, 0.95)',
    starColor2: 'rgba(40, 30, 60, 0.7)',
    lineColor: '110, 31, 161',
    cursorColor: '110, 31, 161',
    maxLinkDist: 160,
    cursorRadius: 220,
    density: 0.00008,
  };

  const cosmosHero = document.getElementById('cosmosHero');
  const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
  const heroCosmosInstance = cosmosHero ? new Cosmos(cosmosHero, {
    ...darkCosmosOpts,
    density: 0.00018,
    cursorRadius: 280,
    maxLinkDist: 200,
    logo: {
      src: '../assets/logo/connectia-white.png',
      widthRatio: isTouchDevice ? 0.7 : 0.42,
      maxWidth: isTouchDevice ? 500 : 720,
      step: isTouchDevice ? 7 : 5,
      revealRadius: isTouchDevice ? 300 : 220,
      decay: isTouchDevice ? 0.005 : 0.0085,
    },
  }) : null;

  // Mobile auto-reveal: sweep a virtual cursor across the logo to reveal it
  if (isTouchDevice && heroCosmosInstance) {
    setTimeout(() => {
      const c = heroCosmosInstance;
      if (!c.logoStars.length) return;
      const cx = c.w / 2, cy = c.h / 2;
      const sweepW = c.w * 0.6;
      let frame = 0;
      const totalFrames = 90;
      function autoReveal() {
        const t = frame / totalFrames;
        c.mouse.x = cx - sweepW / 2 + sweepW * t;
        c.mouse.y = cy + Math.sin(t * Math.PI) * 40;
        c.mouse.active = true;
        frame++;
        if (frame <= totalFrames) {
          requestAnimationFrame(autoReveal);
        } else {
          c.mouse.active = false;
        }
      }
      autoReveal();
    }, 1800);
  }


  // Block 2: white/paper universe — purple stars on light background, full-screen
  const cosmosHeroLight = document.getElementById('cosmosHeroLight');
  if (cosmosHeroLight) new Cosmos(cosmosHeroLight, {
    starColor: 'rgba(110, 31, 161, 0.85)',
    starColor2: 'rgba(40, 30, 60, 0.55)',
    lineColor: '110, 31, 161',
    cursorColor: '110, 31, 161',
    maxLinkDist: 170,
    cursorRadius: 240,
    density: 0.00014,
  });

  // Casos section: cosmic universe with cursor-connecting stars
  const cosmosWork = document.getElementById('cosmosWork');
  if (cosmosWork) new Cosmos(cosmosWork, {
    ...darkCosmosOpts,
    density: 0.0001,
  });

  const cosmosManifesto = document.getElementById('cosmosManifesto');
  if (cosmosManifesto) new Cosmos(cosmosManifesto, darkCosmosOpts);

  const cosmosContact = document.getElementById('cosmosContact');
  if (cosmosContact) new Cosmos(cosmosContact, darkCosmosOpts);

  const cosmosFooter = document.getElementById('cosmosFooter');
  if (cosmosFooter) new Cosmos(cosmosFooter, { ...darkCosmosOpts, density: 0.00012, maxLinkDist: 200, cursorRadius: 280 });

  // Page is visible immediately — no loader/big-bang
  document.body.classList.add('is-loaded', 'is-revealed');

  // NAV
  const menuBtn = document.getElementById('menuBtn');
  const nav = document.getElementById('nav');
  const navLinks = nav.querySelectorAll('a');
  menuBtn.addEventListener('click', () => {
    document.body.classList.toggle('nav-open');
    nav.setAttribute('aria-hidden', !document.body.classList.contains('nav-open'));
  });
  navLinks.forEach(a => a.addEventListener('click', () => {
    document.body.classList.remove('nav-open');
    nav.setAttribute('aria-hidden', 'true');
  }));

  // LANGUAGE TOGGLE
  const langToggle = document.getElementById('langToggle');
  langToggle.addEventListener('click', (e) => {
    const target = e.target.closest('.lang-toggle__opt');
    let next;
    if (target) next = target.dataset.langSet;
    else next = document.documentElement.getAttribute('data-lang') === 'es' ? 'en' : 'es';
    applyLang(next);
  });

  // Auto-scroll to ?goto=<id> after page settles (workaround for hash being clobbered by dynamic layout)
  (function autoScrollFromQuery() {
    try {
      if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
      const m = location.search.match(/[?&]goto=([^&]+)/);
      if (!m) return;
      const id = decodeURIComponent(m[1]);
      const scrollIt = () => {
        const target = document.getElementById(id);
        if (target) {
          const top = target.getBoundingClientRect().top + window.scrollY;
          window.scrollTo(0, top);
        }
      };
      [50, 200, 500, 1200, 2400, 4000].forEach(t => setTimeout(scrollIt, t));
    } catch (e) { /* noop */ }
  })();

  // HERO MODISMOS ROTATOR — single em, swap textContent
  const rotator = document.getElementById('rotator');
  if (rotator) {
    const words = (rotator.dataset.words || '').split('|').filter(Boolean);
    const em = rotator.querySelector('em');
    let idx = 0;
    if (words.length && em) {
      em.textContent = words[0];
      setInterval(() => {
        em.classList.add('is-out');
        setTimeout(() => {
          idx = (idx + 1) % words.length;
          em.textContent = words[idx];
          em.classList.remove('is-out');
        }, 350);
      }, 1300);
    }
  }

  // HERO SLIDESHOW — fast cycling background images
  const slideshow = document.getElementById('heroSlideshow');
  if (slideshow) {
    const slides = Array.from(slideshow.querySelectorAll('.slide'));
    if (slides.length > 1) {
      let sidx = 0;
      setInterval(() => {
        slides[sidx].classList.remove('is-active');
        sidx = (sidx + 1) % slides.length;
        slides[sidx].classList.add('is-active');
      }, 1100);
    }
  }

  // COSMIC SPOTLIGHT on the giant Connectia logo — cursor reveals universe inside letters
  setupLogoSpotlight(document.getElementById('giantLogo'));

  // BRAIN — central cerebro creativo
  const brainEl = document.getElementById('brain');
  if (brainEl) {
    const brainCanvas = document.getElementById('brainCanvas');
    const brainCore = document.getElementById('brainCore');
    const brainNodes = Array.from(brainEl.querySelectorAll('.brain__node'));
    new Brain(brainEl, brainCanvas, brainCore, brainNodes);
  }

  // OUT OF NOISE — comet cluster particles converge into text on hover
  document.querySelectorAll('.noise-text').forEach(el => new ParticleText(el));

  // MAGNETIC BUTTONS
  setupMagnetic();

  // CLIENT SPOTLIGHT
  setupClientSpotlight();

  // BIG WORDMARK FOOTER — letter wave
  document.querySelectorAll('.bigword--footer').forEach(bw => {
    const letters = bw.querySelectorAll('i:not(.bigword__cluster i)');
    letters.forEach((letter, i) => {
      letter.addEventListener('mouseenter', () => {
        letters.forEach((other, j) => {
          const d = Math.abs(i - j);
          if (d <= 2 && j !== i) {
            other.style.transition = 'transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
            other.style.transform = `translateY(${(2 - d) * -3}px)`;
          }
        });
      });
      letter.addEventListener('mouseleave', () => {
        letters.forEach(other => { other.style.transform = ''; });
      });
    });
  });

  // CUSTOM CURSOR
  const cursor = document.getElementById('cursor');
  const cursorDot = document.getElementById('cursorDot');
  if (cursor && window.matchMedia('(hover: hover)').matches) {
    let mx = 0, my = 0, cx = 0, cy = 0;
    document.addEventListener('mousemove', (e) => {
      mx = e.clientX; my = e.clientY;
      cursorDot.style.transform = `translate(${mx}px, ${my}px) translate(-50%, -50%)`;
    });
    const animate = () => {
      cx += (mx - cx) * 0.18;
      cy += (my - cy) * 0.18;
      cursor.style.transform = `translate(${cx}px, ${cy}px) translate(-50%, -50%)`;
      requestAnimationFrame(animate);
    };
    animate();
    document.querySelectorAll('a, button, .pillar__head, .work-card, .client-cell, .brain__node, .reel-tile, .cell').forEach(el => {
      el.addEventListener('mouseenter', () => cursor.classList.add('is-hover'));
      el.addEventListener('mouseleave', () => cursor.classList.remove('is-hover'));
    });
  }

  // PILLARS ACCORDION — all open by default for full visibility of services
  document.querySelectorAll('.pillar').forEach((pillar) => {
    const head = pillar.querySelector('.pillar__head');
    head.addEventListener('click', () => pillar.classList.toggle('is-open'));
    pillar.classList.add('is-open');
  });

  // WORK CAROUSEL
  const viewport = document.getElementById('workViewport');
  const cards = Array.from(viewport.querySelectorAll('.work-card'));
  const prevBtn = document.getElementById('workPrev');
  const nextBtn = document.getElementById('workNext');
  const counterCurrent = document.getElementById('workCurrent');
  const counterTotal = document.getElementById('workTotal');
  let activeIdx = 0;
  counterTotal.textContent = String(cards.length).padStart(2, '0');
  const scrollToCard = (i) => {
    activeIdx = Math.max(0, Math.min(cards.length - 1, i));
    const card = cards[activeIdx];
    viewport.scrollTo({ left: card.offsetLeft - viewport.offsetLeft, behavior: 'smooth' });
    cards.forEach((c, idx) => c.classList.toggle('is-active', idx === activeIdx));
    counterCurrent.textContent = String(activeIdx + 1).padStart(2, '0');
  };
  prevBtn.addEventListener('click', () => scrollToCard(activeIdx - 1));
  nextBtn.addEventListener('click', () => scrollToCard(activeIdx + 1));
  let scrollTimer;
  viewport.addEventListener('scroll', () => {
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(() => {
      const center = viewport.scrollLeft + viewport.clientWidth / 2;
      let closest = 0, closestDist = Infinity;
      cards.forEach((c, i) => {
        const cardCenter = c.offsetLeft - viewport.offsetLeft + c.offsetWidth / 2;
        const dist = Math.abs(cardCenter - center);
        if (dist < closestDist) { closestDist = dist; closest = i; }
      });
      if (closest !== activeIdx) {
        activeIdx = closest;
        cards.forEach((c, idx) => c.classList.toggle('is-active', idx === activeIdx));
        counterCurrent.textContent = String(activeIdx + 1).padStart(2, '0');
      }
    }, 100);
  });

  // CLOCKS
  function updateClocks() {
    document.querySelectorAll('.clock').forEach(el => {
      const tz = el.dataset.tz;
      try {
        const now = new Date().toLocaleTimeString('es-MX', { timeZone: tz, hour: '2-digit', minute: '2-digit', hour12: false });
        el.textContent = now + ' LOCAL';
      } catch (e) { el.textContent = '--:--'; }
    });
  }
  updateClocks();
  setInterval(updateClocks, 30000);

  // SCROLL REVEAL
  const revealEls = [
    ...document.querySelectorAll('.section__chapter, .origen__title, .origen__chain, .origen__copy, .manifesto__big, .manifesto__sub, .stack__title, .stack__list, .stack__note, .work__carousel, .clientes__title, .clientes__grid, .contact__big, .contact__grid, .footer__top, .hero__wordmark, .footer__wordmark, .brain')
  ];
  revealEls.forEach(el => el.classList.add('reveal'));
  document.querySelectorAll('.pillar__list, .footer__top, .clientes__grid').forEach(el => el.classList.add('reveal-stagger'));
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -10% 0px' });
  revealEls.forEach(el => io.observe(el));
});
