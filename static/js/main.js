/**
 * CaupenRost – Premium Dark UI Animation System v2
 */
(function() {
    'use strict';

    window.CaupenRost = window.CaupenRost || {};

    // ── Particle System ──────────────────────────────────────────
    function initParticles() {
        const canvas = document.getElementById('particleCanvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let W, H, particles = [];

        function resize() {
            W = canvas.width  = window.innerWidth;
            H = canvas.height = window.innerHeight;
        }

        function Particle() { this.reset(); }
        Particle.prototype.reset = function() {
            this.x  = Math.random() * W;
            this.y  = Math.random() * H;
            this.r  = Math.random() * 1.6 + 0.4;
            this.vx = (Math.random() - 0.5) * 0.22;
            this.vy = (Math.random() - 0.5) * 0.22 - 0.08;
            this.alpha = Math.random() * 0.5 + 0.1;
            const palette = ['212,168,67', '200,149,42', '232,197,100', '255,180,80'];
            this.color = palette[Math.floor(Math.random() * palette.length)];
        };
        Particle.prototype.update = function() {
            this.x += this.vx; this.y += this.vy;
            this.alpha -= 0.0007;
            if (this.y < -10 || this.alpha <= 0) this.reset();
        };
        Particle.prototype.draw = function() {
            ctx.save();
            ctx.globalAlpha = Math.max(0, this.alpha);
            ctx.fillStyle = `rgba(${this.color},1)`;
            ctx.shadowColor = `rgba(${this.color},0.8)`;
            ctx.shadowBlur = 6;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        };

        resize();
        window.addEventListener('resize', resize, { passive: true });
        for (let i = 0; i < 70; i++) particles.push(new Particle());

        function loop() {
            ctx.clearRect(0, 0, W, H);
            particles.forEach(p => { p.update(); p.draw(); });
            requestAnimationFrame(loop);
        }
        loop();
    }

    // ── Animated Background Subtle Shift ─────────────────────────
    function initAnimatedBg() {
        let hue = 0;
        const body = document.body;
        function tick() {
            hue = (hue + 0.015) % 360;
            const r = Math.round(12 + Math.sin(hue * Math.PI / 180) * 2);
            const g = Math.round(9  + Math.sin(hue * Math.PI / 180) * 1);
            const b = Math.round(6  + Math.sin(hue * Math.PI / 180) * 1);
            body.style.backgroundColor = `rgb(${r},${g},${b})`;
            requestAnimationFrame(tick);
        }
        tick();
    }

    // ── Smooth Scroll ─────────────────────────────────────────────
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(a => {
            a.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href && href !== '#') {
                    const target = document.querySelector(href);
                    if (target) {
                        e.preventDefault();
                        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }
            });
        });
    }

    // ── Hero Parallax ─────────────────────────────────────────────
    function initParallax() {
        const hImg = document.querySelector('.story-hero-img, .hero-image');
        if (!hImg) return;
        window.addEventListener('scroll', function() {
            const y = window.scrollY;
            if (y < window.innerHeight * 1.2) {
                hImg.style.transform = `translateY(${y * 0.10}px)`;
            }
        }, { passive: true });
    }

    // ── Story Chapter Scroll Reveal ───────────────────────────────
    function initScrollReveal() {
        const revealEls = document.querySelectorAll('.reveal');
        if (!revealEls.length) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, idx) => {
                if (entry.isIntersecting) {
                    // slight stagger for sibling elements
                    const delay = entry.target.dataset.delay || 0;
                    setTimeout(() => {
                        entry.target.classList.add('active');
                    }, delay);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });

        revealEls.forEach((el, i) => {
            // Auto-stagger children inside stagger-children containers
            const parent = el.closest('.stagger-children');
            if (parent) {
                const siblings = parent.querySelectorAll('.reveal');
                siblings.forEach((sib, idx) => {
                    sib.dataset.delay = idx * 90;
                });
            }
            observer.observe(el);
        });
    }

    // ── Story Chapter Progress ────────────────────────────────────
    function initStoryProgress() {
        const chapters = document.querySelectorAll('.story-chapter');
        if (!chapters.length) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('chapter-in-view');
                }
            });
        }, { threshold: 0.2 });

        chapters.forEach(ch => observer.observe(ch));
    }

    // ── Auto-dismiss alerts ───────────────────────────────────────
    function autoDismissAlerts() {
        document.querySelectorAll('.alert:not(.alert-permanent)').forEach(a => {
            setTimeout(() => {
                a.style.transition = 'all 0.4s ease';
                a.style.opacity = '0';
                a.style.transform = 'translateY(-10px)';
                setTimeout(() => { if (a.parentNode) a.remove(); }, 400);
            }, 5000);
        });
    }

    // ── Form loading states ───────────────────────────────────────
    function initFormLoading() {
        document.addEventListener('submit', function(e) {
            const form = e.target;
            if (form.classList.contains('needs-loading')) {
                const btn = form.querySelector('button[type="submit"]');
                if (btn) {
                    btn.setAttribute('data-orig', btn.innerHTML);
                    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing…';
                    btn.disabled = true;
                    setTimeout(() => { btn.disabled = false; btn.innerHTML = btn.getAttribute('data-orig'); }, 8000);
                }
            }
        });
    }

    // ── Tooltip init ─────────────────────────────────────────────
    function initTooltips() {
        if (typeof bootstrap !== 'undefined') {
            document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
                new bootstrap.Tooltip(el);
            });
        }
    }

    // ── Page-specific logic ───────────────────────────────────────
    function handlePageLogic() {
        const path = window.location.pathname;
        if (path === '/') {
            document.querySelectorAll('[data-count]').forEach(el => {
                const target = parseInt(el.dataset.count);
                let current = 0;
                const step = target / 60;
                const timer = setInterval(() => {
                    current = Math.min(current + step, target);
                    el.textContent = Math.round(current).toLocaleString();
                    if (current >= target) clearInterval(timer);
                }, 20);
            });
        }
        if (path.includes('/admin')) {
            initAdminCharts();
        }
    }

    function initAdminCharts() {
        if (typeof Chart === 'undefined') return;
        Chart.defaults.color = '#b89870';
        Chart.defaults.borderColor = 'rgba(212,168,67,0.12)';

        const salesCanvas = document.getElementById('salesChart');
        if (salesCanvas) {
            new Chart(salesCanvas.getContext('2d'), {
                type: 'line',
                data: {
                    labels: ['Jan','Feb','Mar','Apr','May','Jun'],
                    datasets: [{
                        label: 'Sales (₹)',
                        data: [12000, 19000, 15000, 25000, 22000, 30000],
                        borderColor: '#e07832',
                        backgroundColor: 'rgba(224,120,50,0.08)',
                        borderWidth: 2,
                        tension: 0.45,
                        fill: true,
                        pointBackgroundColor: '#e07832',
                        pointBorderColor: '#0c0a07',
                        pointBorderWidth: 2,
                        pointRadius: 5,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { color: 'rgba(224,120,50,0.08)' } },
                        y: { grid: { color: 'rgba(224,120,50,0.08)' } }
                    }
                }
            });
        }

        const visCanvas = document.getElementById('visitorsChart');
        if (visCanvas) {
            new Chart(visCanvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
                    datasets: [{
                        label: 'Visitors',
                        data: [12, 19, 15, 25, 22, 30, 28],
                        backgroundColor: 'rgba(224,120,50,0.25)',
                        borderColor: '#e07832',
                        borderWidth: 1.5,
                        borderRadius: 6,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { color: 'rgba(224,120,50,0.08)' } },
                        y: { grid: { color: 'rgba(224,120,50,0.08)' } }
                    }
                }
            });
        }
    }

    // ── Product card 3D tilt ──────────────────────────────────────
    function initCardTilt() {
        document.querySelectorAll('.product-card').forEach(card => {
            card.addEventListener('mousemove', function(e) {
                const rect = card.getBoundingClientRect();
                const x = (e.clientX - rect.left) / rect.width - 0.5;
                const y = (e.clientY - rect.top) / rect.height - 0.5;
                card.style.transform = `translateY(-8px) scale(1.01) rotateX(${-y * 6}deg) rotateY(${x * 6}deg)`;
            });
            card.addEventListener('mouseleave', function() {
                card.style.transition = 'transform 0.5s cubic-bezier(0.4,0,0.2,1)';
                card.style.transform = '';
            });
            card.addEventListener('mouseenter', function() {
                card.style.transition = 'transform 0.1s ease';
            });
        });
    }

    // ── Custom Bakery Cursor ──────────────────────────────────────
    function initBakeryCursor() {
        if (window.matchMedia('(hover: none)').matches) return;

        const cursor = document.createElement('div');
        cursor.className = 'bakery-cursor';
        cursor.textContent = '🥐';
        document.body.appendChild(cursor);

        const trail = document.createElement('div');
        trail.className = 'bakery-cursor-trail';
        document.body.appendChild(trail);

        let mx = -100, my = -100, tx = -100, ty = -100;

        document.addEventListener('mousemove', (e) => {
            mx = e.clientX; my = e.clientY;
            cursor.style.left = mx + 'px';
            cursor.style.top  = my + 'px';
        });

        function trailLoop() {
            tx += (mx - tx) * 0.18;
            ty += (my - ty) * 0.18;
            trail.style.left = tx + 'px';
            trail.style.top  = ty + 'px';
            requestAnimationFrame(trailLoop);
        }
        trailLoop();

        document.querySelectorAll('a, button, .product-card, .story-cat-card, .slider-btn, .quick-action-btn').forEach(el => {
            el.addEventListener('mouseenter', () => cursor.classList.add('hover'));
            el.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
        });

        document.addEventListener('mouseleave', () => { cursor.style.opacity = '0'; trail.style.opacity = '0'; });
        document.addEventListener('mouseenter', () => { cursor.style.opacity = '1'; trail.style.opacity = '1'; });
    }

    // ── Touch Ripple ─────────────────────────────────────────────
    function initTouchRipple() {
        document.addEventListener('touchstart', function(e) {
            const touch = e.touches[0];
            const ripple = document.createElement('div');
            ripple.className = 'touch-ripple';
            ripple.style.left = touch.clientX + 'px';
            ripple.style.top  = touch.clientY + 'px';
            document.body.appendChild(ripple);
            setTimeout(() => { if (ripple.parentNode) ripple.remove(); }, 600);
        }, { passive: true });
    }

    // ── Review Slider ─────────────────────────────────────────────
    function initReviewSlider() {
        const slider = document.getElementById('reviewsSlider');
        if (!slider) return;
        const slides = slider.querySelectorAll('.review-slide');
        if (!slides.length) return;

        function perView() {
            if (window.innerWidth < 576) return 1;
            if (window.innerWidth < 992) return 2;
            return 3;
        }

        let current = 0;
        const total = slides.length;

        function goTo(idx) {
            const pv = perView();
            const maxIdx = Math.max(0, total - pv);
            current = Math.max(0, Math.min(idx, maxIdx));
            const pct = current * (100 / pv);
            slider.style.transform = 'translateX(-' + pct + '%)';
            document.querySelectorAll('.slider-dot').forEach((d, i) => {
                d.classList.toggle('active', i === current);
            });
        }

        window.slideReviews = function(dir) { goTo(current + dir); };

        const dotsContainer = document.getElementById('reviewDots');
        if (dotsContainer) {
            const dotCount = Math.max(1, total - perView() + 1);
            for (let i = 0; i < dotCount; i++) {
                const dot = document.createElement('button');
                dot.className = 'slider-dot' + (i === 0 ? ' active' : '');
                dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
                (function(idx){ dot.addEventListener('click', function() { goTo(idx); }); })(i);
                dotsContainer.appendChild(dot);
            }
        }

        let autoSlide = setInterval(() => goTo(current + 1), 4500);
        slider.parentElement.addEventListener('mouseenter', () => clearInterval(autoSlide));
        slider.parentElement.addEventListener('mouseleave', () => {
            clearInterval(autoSlide);
            autoSlide = setInterval(() => goTo(current + 1), 4500);
        });

        let startX = 0;
        slider.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; }, { passive: true });
        slider.addEventListener('touchend', (e) => {
            const diff = startX - e.changedTouches[0].clientX;
            if (Math.abs(diff) > 45) goTo(current + (diff > 0 ? 1 : -1));
        }, { passive: true });

        window.addEventListener('resize', () => goTo(0));
    }

    // ── Scroll Progress Line ──────────────────────────────────────
    function initScrollProgress() {
        const bar = document.createElement('div');
        bar.style.cssText = 'position:fixed;top:0;left:0;height:2px;background:linear-gradient(90deg,#e07832,#f09248);z-index:99999;width:0%;transition:width 0.1s linear;pointer-events:none;';
        document.body.appendChild(bar);
        window.addEventListener('scroll', function() {
            const scrolled = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
            bar.style.width = scrolled + '%';
        }, { passive: true });
    }

    // ── Story Hero Orbit Animation ────────────────────────────────
    function initOrbitDots() {
        const orbitRing = document.querySelector('.orbit-ring');
        const dots = document.querySelectorAll('.orbit-dot');
        if (!orbitRing || !dots.length) return;

        let angle = 0;
        const radius = orbitRing.offsetWidth / 2;

        function animateDots() {
            angle += 0.3;
            dots.forEach((dot, i) => {
                const offset = (angle + i * 120) * Math.PI / 180;
                const x = Math.cos(offset) * (radius) + radius - 3.5;
                const y = Math.sin(offset) * (radius) + radius - 3.5;
                dot.style.left = x + 'px';
                dot.style.top  = y + 'px';
                dot.style.animation = 'none';
            });
            requestAnimationFrame(animateDots);
        }
        animateDots();
    }

    // ── Page Transition System ────────────────────────────────────
    function initPageTransitions() {
        const overlay = document.getElementById('pageTransitionOverlay');
        if (!overlay) return;

        // Fade in on page load
        overlay.classList.remove('exit');

        // Intercept internal link clicks
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a[href]');
            if (!link) return;
            const href = link.getAttribute('href');
            if (!href || href.startsWith('#') || href.startsWith('mailto:') ||
                href.startsWith('tel:') || href.startsWith('javascript:') ||
                link.hasAttribute('data-bs-toggle') || link.target === '_blank') return;
            if (href.startsWith('http') && !href.includes(window.location.hostname)) return;

            e.preventDefault();
            overlay.classList.add('exit');
            setTimeout(() => { window.location.href = href; }, 300);
        });

        // Back button
        window.addEventListener('pageshow', function(e) {
            if (e.persisted) overlay.classList.remove('exit');
        });
    }

    // ── Counter Animation ─────────────────────────────────────────
    function initCounters() {
        const counters = document.querySelectorAll('.counter-number[data-target]');
        if (!counters.length) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                const el = entry.target;
                const target = parseInt(el.getAttribute('data-target'));
                const isDecimal = el.hasAttribute('data-decimal');
                const duration = 1800;
                const steps = 60;
                const stepTime = duration / steps;
                let current = 0;
                const increment = target / steps;

                const timer = setInterval(() => {
                    current = Math.min(current + increment, target);
                    if (isDecimal) {
                        el.textContent = (current / 10).toFixed(1);
                    } else {
                        el.textContent = Math.round(current).toLocaleString('en-IN');
                    }
                    if (current >= target) clearInterval(timer);
                }, stepTime);

                observer.unobserve(el);
            });
        }, { threshold: 0.3 });

        counters.forEach(el => observer.observe(el));
    }

    // ── Enhanced Cursor with Multiple Emojis ─────────────────────
    function initEnhancedCursor() {
        if (window.matchMedia('(hover: none)').matches) return;

        const emojis = ['🥐', '🎂', '🍞', '🥖', '🍰'];
        let emojiIndex = 0;

        const cursor = document.createElement('div');
        cursor.className = 'bakery-cursor';
        cursor.textContent = emojis[0];
        document.body.appendChild(cursor);

        const trail = document.createElement('div');
        trail.className = 'bakery-cursor-trail';
        document.body.appendChild(trail);

        let mx = -100, my = -100, tx = -100, ty = -100;

        document.addEventListener('mousemove', (e) => {
            mx = e.clientX; my = e.clientY;
            cursor.style.left = mx + 'px';
            cursor.style.top  = my + 'px';
        });

        function trailLoop() {
            tx += (mx - tx) * 0.16;
            ty += (my - ty) * 0.16;
            trail.style.left = tx + 'px';
            trail.style.top  = ty + 'px';
            requestAnimationFrame(trailLoop);
        }
        trailLoop();

        // Rotate emoji on click
        document.addEventListener('click', () => {
            emojiIndex = (emojiIndex + 1) % emojis.length;
            cursor.textContent = emojis[emojiIndex];
            cursor.style.transition = 'transform 0.2s cubic-bezier(0.34,1.56,0.64,1)';
            cursor.style.transform = 'translate(-50%,-50%) scale(1.6) rotate(20deg)';
            setTimeout(() => { cursor.style.transform = ''; cursor.style.transition = ''; }, 300);
        });

        document.querySelectorAll('a, button, .product-card, .story-cat-card, .cat-cinema-card, .slider-btn, .quick-action-btn, .counter-card').forEach(el => {
            el.addEventListener('mouseenter', () => cursor.classList.add('hover'));
            el.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
        });

        document.addEventListener('mouseleave', () => { cursor.style.opacity = '0'; trail.style.opacity = '0'; });
        document.addEventListener('mouseenter', () => { cursor.style.opacity = '1'; trail.style.opacity = '1'; });
    }

    // ── Navbar Active State Enhancement ──────────────────────────
    function initNavbarActive() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            if (link.classList.contains('active')) {
                link.style.color = 'var(--cream)';
            }
        });
    }

    // ── Stagger Children Delay ────────────────────────────────────
    function initStaggerChildren() {
        document.querySelectorAll('.stagger-children').forEach(parent => {
            parent.querySelectorAll('.reveal').forEach((el, idx) => {
                if (!el.dataset.delay) el.dataset.delay = idx * 80;
            });
        });
    }

    // ── Init ──────────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function() {
        initParticles();
        initAnimatedBg();
        initSmoothScroll();
        initParallax();
        initScrollReveal();
        initStoryProgress();
        autoDismissAlerts();
        initFormLoading();
        initTooltips();
        handlePageLogic();
        initCardTilt();
        initEnhancedCursor();
        initTouchRipple();
        initReviewSlider();
        initScrollProgress();
        initOrbitDots();
        initPageTransitions();
        initCounters();
        initNavbarActive();
        initStaggerChildren();
    });

    // ── Utils ─────────────────────────────────────────────────────
    window.CaupenRost.utils = {
        formatCurrency: (n) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(n),
        formatDate: (d) => new Intl.DateTimeFormat('en-IN', { year:'numeric', month:'long', day:'numeric' }).format(new Date(d)),
    };
})();
