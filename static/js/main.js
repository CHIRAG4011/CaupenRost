/**
 * CaupenRost – Premium Dark UI Animation System
 */
(function() {
    'use strict';

    window.CaupenRost = window.CaupenRost || {};

    // ── Particle System ──────────────────────────────────────────
    function initParticles() {
        const canvas = document.getElementById('particleCanvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let W, H, particles = [], animId;

        function resize() {
            W = canvas.width  = window.innerWidth;
            H = canvas.height = window.innerHeight;
        }

        function Particle() {
            this.reset();
        }
        Particle.prototype.reset = function() {
            this.x  = Math.random() * W;
            this.y  = Math.random() * H;
            this.r  = Math.random() * 1.6 + 0.4;
            this.vx = (Math.random() - 0.5) * 0.25;
            this.vy = (Math.random() - 0.5) * 0.25 - 0.1;
            this.alpha = Math.random() * 0.5 + 0.1;
            const palette = ['212,168,67', '200,149,42', '232,197,100', '255,180,80'];
            this.color = palette[Math.floor(Math.random() * palette.length)];
        };
        Particle.prototype.update = function() {
            this.x += this.vx;
            this.y += this.vy;
            this.alpha -= 0.0008;
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

        for (let i = 0; i < 80; i++) particles.push(new Particle());

        function loop() {
            ctx.clearRect(0, 0, W, H);
            particles.forEach(p => { p.update(); p.draw(); });
            animId = requestAnimationFrame(loop);
        }
        loop();
    }

    // ── Animated Background Gradient ────────────────────────────
    function initAnimatedBg() {
        let hue = 0;
        const body = document.body;
        function tick() {
            hue = (hue + 0.02) % 360;
            const r = Math.round(12  + Math.sin(hue * Math.PI / 180) * 2);
            const g = Math.round(10  + Math.sin(hue * Math.PI / 180) * 1);
            const b = Math.round(7   + Math.sin(hue * Math.PI / 180) * 1);
            body.style.backgroundColor = `rgb(${r},${g},${b})`;
            requestAnimationFrame(tick);
        }
        tick();
    }

    // ── Smooth Scroll ────────────────────────────────────────────
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

    // ── Parallax on scroll ────────────────────────────────────────
    function initParallax() {
        const hImg = document.querySelector('.hero-image');
        if (!hImg) return;
        window.addEventListener('scroll', function() {
            const y = window.scrollY;
            hImg.style.transform = `translateY(${y * 0.12}px)`;
        }, { passive: true });
    }

    // ── Stagger entrance for product grids ──────────────────────
    function initStaggeredEntrance() {
        const grids = document.querySelectorAll('.row.g-4');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const children = entry.target.querySelectorAll('.reveal');
                    children.forEach((child, i) => {
                        setTimeout(() => {
                            child.classList.add('active');
                        }, i * 90);
                    });
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.08 });
        grids.forEach(g => observer.observe(g));
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

    // ── Skeleton shimmer on images ────────────────────────────────
    function initLazyImages() {
        document.querySelectorAll('img[data-src]').forEach(img => {
            const wrapper = img.parentElement;
            if (wrapper) wrapper.classList.add('skeleton');
            img.onload = () => { if (wrapper) wrapper.classList.remove('skeleton'); };
            img.src = img.dataset.src;
        });
    }

    // ── Page-specific ─────────────────────────────────────────────
    function handlePageLogic() {
        const path = window.location.pathname;

        if (path === '/') {
            // Counter animation for hero stats
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
                        borderColor: '#d4a843',
                        backgroundColor: 'rgba(212,168,67,0.08)',
                        borderWidth: 2,
                        tension: 0.45,
                        fill: true,
                        pointBackgroundColor: '#d4a843',
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
                        x: { grid: { color: 'rgba(212,168,67,0.08)' } },
                        y: { grid: { color: 'rgba(212,168,67,0.08)' } }
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
                        backgroundColor: 'rgba(212,168,67,0.25)',
                        borderColor: '#d4a843',
                        borderWidth: 1.5,
                        borderRadius: 6,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { color: 'rgba(212,168,67,0.08)' } },
                        y: { grid: { color: 'rgba(212,168,67,0.08)' } }
                    }
                }
            });
        }
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

        document.querySelectorAll('a, button, .product-card, .category-card, .slider-btn, .quick-action-btn').forEach(el => {
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
        slider.addEventListener('mouseenter', () => clearInterval(autoSlide));
        slider.addEventListener('mouseleave', () => {
            clearInterval(autoSlide);
            autoSlide = setInterval(() => goTo(current + 1), 4500);
        });

        let startX = 0;
        slider.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; }, { passive: true });
        slider.addEventListener('touchend',   (e) => {
            const diff = startX - e.changedTouches[0].clientX;
            if (Math.abs(diff) > 45) goTo(current + (diff > 0 ? 1 : -1));
        }, { passive: true });

        window.addEventListener('resize', () => goTo(0));
    }

    // ── Init ──────────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function() {
        initParticles();
        initAnimatedBg();
        initSmoothScroll();
        initParallax();
        initStaggeredEntrance();
        autoDismissAlerts();
        initFormLoading();
        initTooltips();
        initLazyImages();
        handlePageLogic();
        initBakeryCursor();
        initTouchRipple();
        initReviewSlider();
    });

    // Expose globals
    window.CaupenRost.utils = {
        formatCurrency: (n) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(n),
        formatDate: (d) => new Intl.DateTimeFormat('en-IN', { year:'numeric', month:'long', day:'numeric' }).format(new Date(d)),
    };
})();
