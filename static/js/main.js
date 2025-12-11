/**
 * CaupenRost - Main JavaScript
 * Core functionality and utility functions
 */

(function() {
    'use strict';

    // Application namespace
    window.CaupenRost = window.CaupenRost || {};

    /**
     * Main application class
     */
    class BakeryApp {
        constructor() {
            this.init();
        }

        init() {
            this.bindGlobalEvents();
            this.initializeComponents();
            this.handlePageSpecificLogic();
        }

        bindGlobalEvents() {
            // Handle form submissions with loading states
            document.addEventListener('submit', (e) => {
                const form = e.target;
                if (form.classList.contains('needs-loading')) {
                    this.showFormLoading(form);
                }
            });

            // Handle AJAX links
            document.addEventListener('click', (e) => {
                if (e.target.classList.contains('ajax-link')) {
                    e.preventDefault();
                    this.handleAjaxLink(e.target);
                }
            });

            // Auto-dismiss alerts
            document.addEventListener('DOMContentLoaded', () => {
                this.autoDismissAlerts();
            });



            // Handle tooltip initialization
            this.initializeTooltips();

            // Handle modal events
            this.bindModalEvents();

            // Smooth scrolling for anchor links
            this.initializeSmoothScrolling();
        }

        initializeComponents() {
            // Initialize star ratings
            this.initializeStarRatings();

            // Initialize image lazy loading
            this.initializeLazyLoading();

            // Initialize search functionality
            this.initializeSearch();

            // Initialize form validation
            this.initializeFormValidation();
        }

        handlePageSpecificLogic() {
            const path = window.location.pathname;

            switch (true) {
                case path.includes('/products'):
                    this.initializeProductsPage();
                    break;
                case path.includes('/admin'):
                    this.initializeAdminPage();
                    break;
                case path.includes('/checkout'):
                    this.initializeCheckoutPage();
                    break;
                case path === '/':
                    this.initializeHomePage();
                    break;
            }
        }

        // Form handling
        showFormLoading(form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                submitBtn.disabled = true;

                // Store original text for potential restoration
                submitBtn.setAttribute('data-original-text', originalText);
            }
        }

        restoreFormButton(form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.getAttribute('data-original-text');
                if (originalText) {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }
            }
        }

        // Alert handling
        autoDismissAlerts() {
            const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
            alerts.forEach(alert => {
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.classList.remove('show');
                        setTimeout(() => alert.remove(), 150);
                    }
                }, 5000);
            });
        }

        showAlert(message, type = 'info', permanent = false) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show ${permanent ? 'alert-permanent' : ''}`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;

            const container = document.querySelector('.container') || document.body;
            container.insertBefore(alertDiv, container.firstChild);

            if (!permanent) {
                setTimeout(() => {
                    if (alertDiv.parentNode) {
                        alertDiv.remove();
                    }
                }, 5000);
            }
        }

        // Star rating functionality
        initializeStarRatings() {
            document.querySelectorAll('.star-rating').forEach(rating => {
                const stars = rating.querySelectorAll('.star');
                const input = rating.querySelector('input[type="hidden"]');

                stars.forEach((star, index) => {
                    star.addEventListener('click', () => {
                        const value = index + 1;
                        if (input) input.value = value;

                        stars.forEach((s, i) => {
                            s.classList.toggle('active', i < value);
                        });
                    });

                    star.addEventListener('mouseenter', () => {
                        stars.forEach((s, i) => {
                            s.classList.toggle('hover', i <= index);
                        });
                    });
                });

                rating.addEventListener('mouseleave', () => {
                    stars.forEach(s => s.classList.remove('hover'));
                });
            });
        }

        // Image lazy loading
        initializeLazyLoading() {
            if ('IntersectionObserver' in window) {
                const imageObserver = new IntersectionObserver((entries, observer) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const img = entry.target;
                            img.src = img.dataset.src;
                            img.classList.remove('lazy');
                            observer.unobserve(img);
                        }
                    });
                });

                document.querySelectorAll('img[data-src]').forEach(img => {
                    imageObserver.observe(img);
                });
            } else {
                // Fallback for older browsers
                document.querySelectorAll('img[data-src]').forEach(img => {
                    img.src = img.dataset.src;
                });
            }
        }

        // Search functionality
        initializeSearch() {
            const searchInputs = document.querySelectorAll('.search-input');
            searchInputs.forEach(input => {
                let searchTimeout;

                input.addEventListener('input', (e) => {
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(() => {
                        this.performSearch(e.target.value, e.target);
                    }, 300);
                });
            });
        }

        performSearch(query, input) {
            const searchContainer = input.closest('.search-container');
            const resultsContainer = searchContainer?.querySelector('.search-results');

            if (!resultsContainer || query.length < 2) {
                if (resultsContainer) resultsContainer.style.display = 'none';
                return;
            }

            // Show loading
            resultsContainer.innerHTML = '<div class="p-3"><i class="fas fa-spinner fa-spin"></i> Searching...</div>';
            resultsContainer.style.display = 'block';

            // Simulate search (replace with actual search endpoint)
            setTimeout(() => {
                resultsContainer.innerHTML = `
                    <div class="p-3">
                        <div class="search-result-item">Sample result for "${query}"</div>
                    </div>
                `;
            }, 500);
        }

        // Form validation
        initializeFormValidation() {
            const forms = document.querySelectorAll('.needs-validation');
            forms.forEach(form => {
                form.addEventListener('submit', (e) => {
                    if (!form.checkValidity()) {
                        e.preventDefault();
                        e.stopPropagation();
                        this.showValidationErrors(form);
                    }
                    form.classList.add('was-validated');
                });
            });
        }

        showValidationErrors(form) {
            const firstInvalid = form.querySelector(':invalid');
            if (firstInvalid) {
                firstInvalid.focus();
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }

        // Tooltip initialization
        initializeTooltips() {
            if (typeof bootstrap !== 'undefined') {
                const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
            }
        }

        // Modal events
        bindModalEvents() {
            document.addEventListener('shown.bs.modal', (e) => {
                const modal = e.target;
                const firstInput = modal.querySelector('input, textarea, select');
                if (firstInput) firstInput.focus();
            });

            document.addEventListener('hidden.bs.modal', (e) => {
                const modal = e.target;
                const form = modal.querySelector('form');
                if (form) {
                    form.reset();
                    form.classList.remove('was-validated');
                }
            });
        }

        // Smooth scrolling
        initializeSmoothScrolling() {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', (e) => {
                    e.preventDefault();
                    const href = anchor.getAttribute('href');
                    if (href && href !== '#') {
                        const target = document.querySelector(href);
                        if (target) {
                            target.scrollIntoView({ behavior: 'smooth' });
                        }
                    }
                });
            });
        }

        // Page-specific initializations
        initializeProductsPage() {
            // Product filter functionality
            const filterButtons = document.querySelectorAll('.filter-btn');
            filterButtons.forEach(btn => {
                btn.addEventListener('click', () => {
                    this.filterProducts(btn.dataset.category);
                });
            });

            // Product comparison
            this.initializeProductComparison();
        }

        initializeAdminPage() {
            // Admin-specific functionality
            this.initializeDataTables();
            this.initializeCharts();
        }

        initializeCheckoutPage() {
            // Address selection logic
            const addressRadios = document.querySelectorAll('input[name="address_id"]');
            addressRadios.forEach(radio => {
                radio.addEventListener('change', (e) => {
                    this.updateShippingPreview(e.target.value);
                });
            });

            // Payment form validation
            this.initializePaymentValidation();
        }

        initializeHomePage() {
            // Hero section animations
            this.animateHeroElements();

            // Featured products carousel
            this.initializeFeaturedCarousel();
        }

        // Utility methods
        filterProducts(category) {
            const products = document.querySelectorAll('.product-card');
            products.forEach(product => {
                const productCategory = product.dataset.category;
                if (category === 'all' || productCategory === category) {
                    product.style.display = 'block';
                    product.classList.add('fade-in');
                } else {
                    product.style.display = 'none';
                }
            });
        }

        initializeProductComparison() {
            const compareButtons = document.querySelectorAll('.compare-btn');
            let compareList = JSON.parse(localStorage.getItem('compareList') || '[]');

            compareButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const productId = e.target.dataset.productId;
                    if (compareList.includes(productId)) {
                        compareList = compareList.filter(id => id !== productId);
                        btn.classList.remove('active');
                    } else if (compareList.length < 3) {
                        compareList.push(productId);
                        btn.classList.add('active');
                    } else {
                        this.showAlert('You can compare up to 3 products at a time', 'warning');
                    }

                    localStorage.setItem('compareList', JSON.stringify(compareList));
                    this.updateCompareCounter();
                });
            });
        }

        updateCompareCounter() {
            const counter = document.querySelector('.compare-counter');
            const compareList = JSON.parse(localStorage.getItem('compareList') || '[]');
            if (counter) {
                counter.textContent = compareList.length;
                counter.style.display = compareList.length > 0 ? 'inline' : 'none';
            }
        }

        initializeCharts() {
            // Initialize charts for admin dashboard
            if (typeof Chart !== 'undefined') {
                this.initializeSalesChart();
                this.initializeVisitorsChart();
            }
        }

        initializeSalesChart() {
            const canvas = document.getElementById('salesChart');
            if (!canvas) return;

            const ctx = canvas.getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Sales (₹)',
                        data: [12000, 19000, 15000, 25000, 22000, 30000],
                        borderColor: 'rgb(139, 69, 19)',
                        backgroundColor: 'rgba(139, 69, 19, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }

        initializeVisitorsChart() {
            const canvas = document.getElementById('visitorsChart');
            if (!canvas) return;

            const ctx = canvas.getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Visitors',
                        data: [12, 19, 15, 25, 22, 30, 28],
                        backgroundColor: 'rgba(139, 69, 19, 0.6)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }

        initializeDataTables() {
            // Simple table sorting and filtering
            const tables = document.querySelectorAll('.data-table');
            tables.forEach(table => {
                this.makeSortable(table);
            });
        }

        makeSortable(table) {
            const headers = table.querySelectorAll('th[data-sortable]');
            headers.forEach(header => {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    this.sortTable(table, header);
                });
            });
        }

        sortTable(table, header) {
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const columnIndex = Array.from(header.parentNode.children).indexOf(header);
            const isAscending = header.classList.contains('sort-asc');

            rows.sort((a, b) => {
                const aValue = a.children[columnIndex].textContent.trim();
                const bValue = b.children[columnIndex].textContent.trim();
                
                if (isAscending) {
                    return bValue.localeCompare(aValue, undefined, { numeric: true });
                } else {
                    return aValue.localeCompare(bValue, undefined, { numeric: true });
                }
            });

            // Update header classes
            table.querySelectorAll('th').forEach(th => th.classList.remove('sort-asc', 'sort-desc'));
            header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');

            // Reorder rows
            rows.forEach(row => tbody.appendChild(row));
        }

        animateHeroElements() {
            const heroElements = document.querySelectorAll('.hero-section .fade-in');
            heroElements.forEach((element, index) => {
                setTimeout(() => {
                    element.classList.add('animated');
                }, index * 200);
            });
        }

        initializeFeaturedCarousel() {
            // Simple carousel functionality if needed
            const carousel = document.querySelector('.featured-carousel');
            if (carousel) {
                // Carousel logic here
            }
        }

        updateShippingPreview(addressId) {
            const preview = document.querySelector('.shipping-preview');
            if (preview) {
                preview.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Updating...`;
                
                setTimeout(() => {
                    preview.innerHTML = `<i class="fas fa-check text-success"></i> Shipping address updated`;
                }, 1000);
            }
        }

        initializePaymentValidation() {
            const cardInput = document.querySelector('#cardNumber');
            if (cardInput) {
                cardInput.addEventListener('input', (e) => {
                    // Format card number
                    let value = e.target.value.replace(/\D/g, '');
                    value = value.replace(/(\d{4})(?=\d)/g, '$1 ');
                    e.target.value = value;
                });
            }
        }

        // Utility functions
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }

        throttle(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }

        formatCurrency(amount) {
            return new Intl.NumberFormat('en-IN', {
                style: 'currency',
                currency: 'INR'
            }).format(amount);
        }

        formatDate(date) {
            return new Intl.DateTimeFormat('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }).format(new Date(date));
        }
    }

    // Initialize the application
    document.addEventListener('DOMContentLoaded', () => {
        window.CaupenRost.app = new BakeryApp();
    });

    // Expose utilities globally
    window.CaupenRost.utils = {
        formatCurrency: (amount) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount),
        formatDate: (date) => new Intl.DateTimeFormat('en-IN', { year: 'numeric', month: 'long', day: 'numeric' }).format(new Date(date)),
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    };

})();
