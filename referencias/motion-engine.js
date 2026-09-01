/**
 * AHOLIC MOTION ENGINE v2.0
 * Motor de animações cinematográficas para todos os sites Aholic Digital.
 * Injetar antes do </body> em qualquer site gerado.
 *
 * Funcionalidades:
 *  - Preloader cinematic curtain com nome do cliente
 *  - Scroll reveal escalonado com IntersectionObserver
 *  - Cursor magnético customizado (cor do cliente via CSS var)
 *  - Contador numérico animado
 *  - Hover parallax em cards/imagens
 *  - Floating badge bounce
 *  - Marquee ribbon infinita
 *  - Header hide-on-scroll
 */

(function AholicMotionEngine() {
    'use strict';

    /* ─── 0. Configuração ──────────────────────────────────────────────── */
    const CONFIG = {
        preloader: {
            enabled: true,
            duration: 1800,         // ms total do preloader
            curtainDuration: 600,   // ms da animação da cortina
        },
        cursor: {
            enabled: window.innerWidth > 768,
            labelHover: 'VER',
        },
        reveal: {
            threshold: 0.10,
            staggerMs: 120,
        },
        counters: {
            duration: 1600,
            easing: 'easeOutExpo',
        },
        parallax: {
            enabled: true,
            strength: 0.04,
        },
    };

    /* ─── 1. Inject CSS ─────────────────────────────────────────────────── */
    const css = `
    /* ── Preloader ── */
    #ah-preloader {
        position: fixed; inset: 0; z-index: 99999;
        display: flex; align-items: center; justify-content: center;
        pointer-events: all;
        overflow: hidden;
    }
    #ah-curtain-left, #ah-curtain-right {
        position: absolute; top: 0; bottom: 0;
        width: 50%;
        background: var(--ah-preloader-bg, #0d0d0d);
        transition: transform var(--ah-curtain-duration, 600ms) cubic-bezier(0.76, 0, 0.24, 1);
    }
    #ah-curtain-left  { left: 0; transform-origin: left; }
    #ah-curtain-right { right: 0; transform-origin: right; }
    #ah-preloader.ah-reveal #ah-curtain-left  { transform: translateX(-100%); }
    #ah-preloader.ah-reveal #ah-curtain-right { transform: translateX(100%); }
    #ah-preloader.ah-done { display: none; }
    #ah-preloader-content {
        position: relative; z-index: 2;
        display: flex; flex-direction: column; align-items: center; gap: 14px;
        color: var(--ah-preloader-text, #f5f5f5);
        font-family: var(--ah-font-display, 'League Spartan', sans-serif);
        text-align: center;
        pointer-events: none;
        transition: opacity 0.4s ease;
    }
    #ah-preloader.ah-reveal #ah-preloader-content { opacity: 0; }
    #ah-preloader-name {
        font-size: clamp(1.5rem, 5vw, 3rem);
        font-weight: 900;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }
    #ah-preloader-sub {
        font-size: 0.7rem;
        letter-spacing: 0.35em;
        text-transform: uppercase;
        opacity: 0.55;
        font-weight: 600;
    }
    #ah-preloader-bar {
        width: 120px; height: 2px;
        background: rgba(255,255,255,0.15);
        border-radius: 99px;
        overflow: hidden;
        margin-top: 4px;
    }
    #ah-preloader-bar-fill {
        height: 100%;
        background: var(--ah-accent, #E0A96D);
        border-radius: 99px;
        width: 0%;
        transition: width var(--ah-preloader-duration, 1200ms) cubic-bezier(0.65, 0, 0.35, 1);
    }

    /* ── Cursor ── */
    #ah-cursor {
        position: fixed; top: 0; left: 0;
        width: 14px; height: 14px; border-radius: 50%;
        background: var(--ah-accent, #E0A96D);
        pointer-events: none; z-index: 98000;
        transform: translate(-50%, -50%);
        transition: width 0.3s, height 0.3s, background 0.3s, opacity 0.3s;
        opacity: 0;
        will-change: left, top;
    }
    #ah-cursor-ring {
        position: fixed; top: 0; left: 0;
        width: 40px; height: 40px; border-radius: 50%;
        border: 1.5px solid var(--ah-accent, #E0A96D);
        opacity: 0.35;
        pointer-events: none; z-index: 97999;
        transform: translate(-50%, -50%);
        transition: width 0.35s cubic-bezier(0.34,1.56,0.64,1),
                    height 0.35s cubic-bezier(0.34,1.56,0.64,1),
                    opacity 0.3s, border-color 0.3s;
        will-change: left, top;
    }
    body:hover #ah-cursor, body:hover #ah-cursor-ring { opacity: 1; }
    #ah-cursor-ring.ah-ring-hover {
        width: 64px; height: 64px; opacity: 0.7;
    }
    #ah-cursor.ah-cursor-hover {
        width: 56px; height: 56px;
        background: var(--ah-accent, #E0A96D);
        opacity: 0.92;
        display: flex; align-items: center; justify-content: center;
        font-size: 9px; font-weight: 900; letter-spacing: 0.12em;
        color: var(--ah-cursor-label-color, #0d0d0d);
        font-family: var(--ah-font-display, 'League Spartan', sans-serif);
        text-transform: uppercase;
    }

    /* ── Reveal ── */
    .ah-reveal-item {
        opacity: 0;
        transform: translateY(36px) scale(0.985);
        transition: opacity 0.85s cubic-bezier(0.16,1,0.3,1),
                    transform 0.85s cubic-bezier(0.16,1,0.3,1);
        will-change: opacity, transform;
    }
    .ah-reveal-item.ah-revealed {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
    .ah-reveal-left  { transform: translateX(-40px) scale(0.98); }
    .ah-reveal-right { transform: translateX(40px) scale(0.98); }
    .ah-reveal-left.ah-revealed,
    .ah-reveal-right.ah-revealed { transform: translateX(0) scale(1); }
    .ah-reveal-scale { transform: scale(0.88); }
    .ah-reveal-scale.ah-revealed { transform: scale(1); }

    /* ── Counter ── */
    .ah-counter { display: inline-block; }

    /* ── Marquee ── */
    .ah-marquee-track {
        display: flex;
        animation: ah-marquee-run 22s linear infinite;
    }
    .ah-marquee-track:hover { animation-play-state: paused; }
    @keyframes ah-marquee-run {
        0%   { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }

    /* ── Float badge ── */
    @keyframes ah-float {
        0%,100% { transform: translateY(-5px); }
        50%      { transform: translateY(5px); }
    }
    .ah-float { animation: ah-float 4s ease-in-out infinite; }

    /* ── Parallax img ── */
    .ah-parallax-wrap { overflow: hidden; }
    .ah-parallax-img  { will-change: transform; }

    /* ── Header on scroll ── */
    .ah-header-scrolled {
        box-shadow: 0 4px 30px rgba(0,0,0,0.25) !important;
    }
    `;

    const styleEl = document.createElement('style');
    styleEl.id = 'ah-motion-styles';
    styleEl.textContent = css;
    document.head.appendChild(styleEl);

    /* ─── 2. Preloader ──────────────────────────────────────────────────── */
    function initPreloader() {
        if (!CONFIG.preloader.enabled) return;

        // Read name from meta or data attribute or document title
        const brandName = document.querySelector('[data-ah-brand]')?.dataset.ahBrand
            || document.querySelector('meta[name="ah-brand"]')?.content
            || document.title.split('|')[0].split('•')[0].split('–')[0].trim()
            || 'AHOLIC';

        const brandSub = document.querySelector('[data-ah-sub]')?.dataset.ahSub
            || document.querySelector('meta[name="ah-sub"]')?.content
            || '';

        const curtainDur = CONFIG.preloader.curtainDuration;
        const totalDur   = CONFIG.preloader.duration;

        document.documentElement.style.setProperty('--ah-curtain-duration', curtainDur + 'ms');
        document.documentElement.style.setProperty('--ah-preloader-duration', (totalDur - 400) + 'ms');

        const preloader = document.createElement('div');
        preloader.id = 'ah-preloader';
        preloader.innerHTML = `
            <div id="ah-curtain-left"></div>
            <div id="ah-curtain-right"></div>
            <div id="ah-preloader-content">
                <div id="ah-preloader-name">${brandName}</div>
                ${brandSub ? `<div id="ah-preloader-sub">${brandSub}</div>` : ''}
                <div id="ah-preloader-bar"><div id="ah-preloader-bar-fill"></div></div>
            </div>
        `;
        document.body.prepend(preloader);

        // Animate bar immediately
        requestAnimationFrame(() => {
            document.getElementById('ah-preloader-bar-fill').style.width = '100%';
        });

        // Open curtains after bar near-complete
        setTimeout(() => {
            preloader.classList.add('ah-reveal');
        }, totalDur - curtainDur - 100);

        // Remove preloader
        setTimeout(() => {
            preloader.classList.add('ah-done');
            document.body.style.overflow = '';
        }, totalDur + 100);

        // Prevent scroll during preloader
        document.body.style.overflow = 'hidden';
    }

    /* ─── 3. Cursor ────────────────────────────────────────────────────── */
    function initCursor() {
        if (!CONFIG.cursor.enabled) return;

        const cursor = document.createElement('div');
        cursor.id = 'ah-cursor';
        const ring = document.createElement('div');
        ring.id = 'ah-cursor-ring';
        document.body.append(cursor, ring);

        let mx = 0, my = 0, rx = 0, ry = 0;

        window.addEventListener('mousemove', e => {
            mx = e.clientX;
            my = e.clientY;
            cursor.style.left = mx + 'px';
            cursor.style.top  = my + 'px';
        });

        (function animateRing() {
            rx += (mx - rx) * 0.14;
            ry += (my - ry) * 0.14;
            ring.style.left = rx + 'px';
            ring.style.top  = ry + 'px';
            requestAnimationFrame(animateRing);
        })();

        const interactiveSelector = 'a, button, [data-ah-hover], .ah-reveal-item, img, .luxury-img-card, .service-card';
        document.querySelectorAll(interactiveSelector).forEach(el => {
            el.addEventListener('mouseenter', () => {
                cursor.classList.add('ah-cursor-hover');
                ring.classList.add('ah-ring-hover');
                cursor.textContent = CONFIG.cursor.labelHover;
            });
            el.addEventListener('mouseleave', () => {
                cursor.classList.remove('ah-cursor-hover');
                ring.classList.remove('ah-ring-hover');
                cursor.textContent = '';
            });
        });
    }

    /* ─── 4. Scroll Reveal ─────────────────────────────────────────────── */
    function initReveal() {
        // Auto-tag elements that don't have ah-reveal-* yet
        const autoTargets = [
            'section > *', 'main > *', 'article > *',
            '.reveal-item', '[data-reveal]',
        ];
        autoTargets.forEach(sel => {
            document.querySelectorAll(sel).forEach((el, i) => {
                if (!el.classList.contains('ah-reveal-item')) {
                    el.classList.add('ah-reveal-item');
                    if (!el.style.transitionDelay) {
                        el.style.transitionDelay = (i % 6) * CONFIG.reveal.staggerMs + 'ms';
                    }
                }
            });
        });

        const io = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('ah-revealed');
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: CONFIG.reveal.threshold });

        document.querySelectorAll('.ah-reveal-item').forEach(el => io.observe(el));
    }

    /* ─── 5. Counters ──────────────────────────────────────────────────── */
    function animateCount(el) {
        const target = parseFloat(el.dataset.ahCount || el.textContent.replace(/[^0-9.]/g, ''));
        const suffix = el.dataset.ahSuffix || el.textContent.replace(/[\d.]/g, '').trim();
        const prefix = el.dataset.ahPrefix || '';
        const decimals = target % 1 !== 0 ? 1 : 0;
        const dur = CONFIG.counters.duration;
        const start = performance.now();

        function tick(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / dur, 1);
            const eased = 1 - Math.pow(1 - progress, 4); // easeOutQuart
            const current = eased * target;
            el.textContent = prefix + current.toFixed(decimals) + suffix;
            if (progress < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    function initCounters() {
        const io = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCount(entry.target);
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        // Auto-detect: elements with data-ah-count or .ah-counter class
        document.querySelectorAll('[data-ah-count], .ah-counter').forEach(el => io.observe(el));

        // Also auto-tag large numbers that look like metrics (e.g. "4.8", "280+", "100%")
        document.querySelectorAll('span, div, p').forEach(el => {
            if (el.children.length > 0) return;
            const text = el.textContent.trim();
            if (/^\d{1,4}[+%★\s]*$/.test(text) || /^\d\.\d\s*★$/.test(text)) {
                if (el.parentElement?.classList.contains('metric') 
                    || el.classList.contains('stat')
                    || el.closest('[class*="metric"]')
                    || el.closest('[class*="stat"]')) {
                    el.classList.add('ah-counter');
                    el.dataset.ahCount = parseFloat(text);
                    el.dataset.ahSuffix = text.replace(/[\d.]/g, '').trim();
                    io.observe(el);
                }
            }
        });
    }

    /* ─── 6. Parallax ──────────────────────────────────────────────────── */
    function initParallax() {
        if (!CONFIG.parallax.enabled || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

        const items = document.querySelectorAll('.ah-parallax-img, [data-ah-parallax]');
        if (!items.length) return;

        window.addEventListener('scroll', () => {
            const sy = window.scrollY;
            items.forEach(el => {
                const strength = parseFloat(el.dataset.ahParallax || CONFIG.parallax.strength);
                const rect = el.getBoundingClientRect();
                const center = rect.top + rect.height / 2;
                const offset = (window.innerHeight / 2 - center) * strength;
                el.style.transform = `translateY(${offset.toFixed(2)}px)`;
            });
        }, { passive: true });
    }

    /* ─── 7. Header hide-on-scroll ─────────────────────────────────────── */
    function initHeader() {
        const header = document.querySelector('header, [data-ah-header]');
        if (!header) return;

        let lastY = 0;
        window.addEventListener('scroll', () => {
            const y = window.scrollY;
            if (y > 80) {
                header.classList.add('ah-header-scrolled');
            } else {
                header.classList.remove('ah-header-scrolled');
            }
            lastY = y;
        }, { passive: true });
    }

    /* ─── 8. Floating badges ────────────────────────────────────────────── */
    function initFloatBadges() {
        document.querySelectorAll('.ah-float, [data-ah-float]').forEach(el => {
            el.style.animationDelay = (Math.random() * 1.5).toFixed(2) + 's';
        });
        // Also auto-apply to the standard floating badge pattern
        document.querySelectorAll('.animate-bounce-slow').forEach(el => {
            el.classList.add('ah-float');
        });
    }

    /* ─── 9. Marquee ────────────────────────────────────────────────────── */
    function initMarquee() {
        // Support both .ah-marquee-track and .animate-marquee (legacy)
        document.querySelectorAll('.animate-marquee').forEach(el => {
            el.classList.add('ah-marquee-track');
        });
    }

    /* ─── Boot ─────────────────────────────────────────────────────────── */
    function boot() {
        initPreloader();
        initCursor();
        initFloatBadges();
        initMarquee();

        // After DOM settles
        requestAnimationFrame(() => {
            initReveal();
            initCounters();
            initParallax();
            initHeader();
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }

})();
