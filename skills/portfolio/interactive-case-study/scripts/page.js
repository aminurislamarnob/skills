/* Interactive case study behaviour, inlined by build_page.py. No library.
   Everything works without it: the HTML carries the "after" figures, the
   busiest bar's note, the first zone's note and every card in the flow. */
(() => {
    const root = document.querySelector('.cs');
    if (!root) return;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const $$ = (sel, el = root) => [...el.querySelectorAll(sel)];

    /* reading progress */
    let ticking = false;
    const measure = () => {
        ticking = false;
        const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
        root.style.setProperty('--cs-progress', `${Math.min(100, (window.scrollY / max) * 100).toFixed(1)}%`);
    };
    const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(measure); } };
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll, { passive: true });
    measure();

    /* hero figures count up */
    const kpis = $$('[data-count]');
    if (!reduce && kpis.length) {
        const targets = kpis.map((el) => Number(el.dataset.count));
        const fmt = new Intl.NumberFormat(document.documentElement.lang || 'en');
        let start = null;
        const step = (ts) => {
            if (start === null) start = ts + 450;
            const t = Math.max(0, Math.min(1, (ts - start) / 1400));
            const e = 1 - Math.pow(1 - t, 3);
            kpis.forEach((el, i) => { el.firstChild.nodeValue = fmt.format(Math.round(targets[i] * e)); });
            if (t < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    }

    /* water buttons lean toward the pointer */
    if (!reduce) {
        const water = (t) => (t instanceof Element ? t.closest('.water') : null);
        document.addEventListener('pointermove', (e) => {
            const b = water(e.target);
            if (!b) return;
            const r = b.getBoundingClientRect();
            b.style.setProperty('--slosh', Math.max(-1, Math.min(1, ((e.clientX - r.left) / r.width) * 2 - 1)).toFixed(3));
        }, { passive: true });
        document.addEventListener('pointerout', (e) => {
            const b = water(e.target);
            if (b && !b.contains(e.relatedTarget)) b.style.setProperty('--slosh', '0');
        }, { passive: true });
    }

    /* 01 timeline: a bar shows its note */
    $$('[data-timeline]').forEach((tl) => {
        const bars = $$('.cs-day', tl);
        const head = tl.querySelector('[data-note-head]');
        const body = tl.querySelector('[data-note-body]');
        bars.forEach((bar) => bar.addEventListener('click', () => {
            bars.forEach((b) => b.setAttribute('aria-pressed', String(b === bar)));
            head.textContent = bar.dataset.head;
            body.textContent = bar.dataset.note;
        }));
    });

    /* 02 architecture: a pill (or a click on the zone) lights one zone */
    $$('[data-zones]').forEach((sec) => {
        const pills = $$('[data-zone-pill]', sec);
        const zones = $$('[data-zone]', sec);
        const note = sec.querySelector('[data-zone-note]');
        const pick = (i) => {
            pills.forEach((p, j) => p.setAttribute('aria-pressed', String(i === j)));
            zones.forEach((z) => z.classList.toggle('is-dim', Number(z.dataset.zone) !== i));
            const p = pills[i];
            if (!p || !note) return;
            // data-body is the builder's escaped inline markup; the title is plain text
            const strong = document.createElement('strong');
            strong.textContent = `${p.dataset.title}:`;
            note.innerHTML = ` ${p.dataset.body}`;
            note.prepend(strong);
        };
        pills.forEach((p, i) => p.addEventListener('click', () => pick(i)));
        zones.forEach((z) => z.addEventListener('click', () => pick(Number(z.dataset.zone))));
    });

    /* 03 decisions: pills jump to a card and follow the one on top */
    $$('[data-deck]').forEach((sec) => {
        const deck = sec.querySelector('.cs-deck');
        const nav = sec.querySelector('.cs-deck-nav');
        const pills = $$('.cs-pill-btn', nav);
        const UNSTUCK = 120;
        const tops = () => {
            const gap = parseFloat(getComputedStyle(deck).rowGap) || 0;
            let y = deck.getBoundingClientRect().top + window.scrollY;
            return [...deck.children].map((card) => {
                const stuck = parseFloat(getComputedStyle(card).top) || UNSTUCK;
                const t = { flow: y, stuck };
                y += card.offsetHeight + gap;
                return t;
            });
        };
        let current = -1;
        const setCurrent = (i) => {
            if (i === current) return;
            current = i;
            pills.forEach((p, j) => (j === i ? p.setAttribute('aria-current', 'true') : p.removeAttribute('aria-current')));
            const pill = pills[i];
            if (pill && nav.scrollWidth > nav.clientWidth) {
                nav.scrollTo({ left: pill.offsetLeft - (nav.clientWidth - pill.offsetWidth) / 2, behavior: reduce ? 'auto' : 'smooth' });
            }
        };
        let raf = 0;
        const track = () => {
            cancelAnimationFrame(raf);
            raf = requestAnimationFrame(() => {
                let top = 0;
                tops().forEach((t, i) => { if (window.scrollY + t.stuck >= t.flow - 2) top = i; });
                setCurrent(top);
            });
        };
        pills.forEach((p, i) => p.addEventListener('click', () => {
            const t = tops()[i];
            if (t) window.scrollTo({ top: t.flow - t.stuck, behavior: reduce ? 'auto' : 'smooth' });
        }));
        addEventListener('scroll', track, { passive: true });
        addEventListener('resize', track, { passive: true });
        track();
    });

    /* 04 results: before / after */
    const C = 2 * Math.PI * 52;
    $$('[data-flip]').forEach((sec) => {
        const flip = sec.querySelector('.cs-flip');
        const btns = $$('.cs-toggle button', sec);
        const gauge = sec.querySelector('.cs-gauge-fill');
        const gval = sec.querySelector('.cs-gauge-value');
        const set = (after) => {
            const key = after ? 'after' : 'before';
            btns.forEach((b) => b.setAttribute('aria-pressed', String((b.dataset.side === 'after') === after)));
            flip.classList.toggle('is-after', after);
            $$('[data-before]', sec).forEach((el) => { el.textContent = el.dataset[key]; });
            if (gauge) {
                const v = Number(gauge.dataset[key]);
                const max = Number(gauge.dataset.max) || 100;
                gauge.style.strokeDashoffset = String(C * (1 - Math.min(1, v / max)));
                gval.textContent = gval.dataset[key];
            }
        };
        btns.forEach((b) => b.addEventListener('click', () => set(b.dataset.side === 'after')));
    });

    /* 05 screens: a small lightbox over every [data-lb] in page order */
    const dlg = document.querySelector('.cs-lb');
    const items = $$('[data-lb]');
    if (dlg && items.length && typeof dlg.showModal === 'function') {
        const img = dlg.querySelector('img');
        const cap = dlg.querySelector('[data-lb-cap]');
        const count = dlg.querySelector('[data-lb-count]');
        let at = 0;
        const show = (i) => {
            at = (i + items.length) % items.length;
            const it = items[at];
            img.classList.toggle('is-long', it.dataset.long === '1');
            img.src = it.dataset.lb;
            img.alt = it.dataset.alt || '';
            cap.textContent = it.dataset.cap || '';
            count.textContent = `${at + 1} / ${items.length}`;
            dlg.querySelector('.cs-lb-stage').scrollTop = 0;
        };
        items.forEach((it, i) => it.addEventListener('click', (e) => { e.preventDefault(); show(i); dlg.showModal(); }));
        $$('[data-lb-open]').forEach((b) => b.addEventListener('click', () => { show(Number(b.dataset.lbOpen) || 0); dlg.showModal(); }));
        dlg.querySelector('.cs-lb-close').addEventListener('click', () => dlg.close());
        dlg.querySelector('.cs-lb-prev').addEventListener('click', () => show(at - 1));
        dlg.querySelector('.cs-lb-next').addEventListener('click', () => show(at + 1));
        dlg.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') show(at - 1);
            if (e.key === 'ArrowRight') show(at + 1);
        });
        dlg.addEventListener('click', (e) => { if (e.target === dlg || e.target.classList.contains('cs-lb-stage')) dlg.close(); });
    }
})();
