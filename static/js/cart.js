/**
 * CaupenRost - Cart Management
 * Uses /api/cart/* JSON endpoints for all cart operations.
 */

class CartManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateCartCount();
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            const addBtn = e.target.closest('.add-to-cart-btn');
            if (addBtn) {
                e.preventDefault();
                this.handleAddToCart(addBtn);
            }
        });

        document.addEventListener('click', (e) => {
            if (e.target.matches('.quantity-minus')) {
                e.preventDefault();
                this.updateQuantity(e.target, -1);
            } else if (e.target.matches('.quantity-plus')) {
                e.preventDefault();
                this.updateQuantity(e.target, 1);
            }
        });

        document.addEventListener('click', (e) => {
            const removeBtn = e.target.closest('.remove-item-btn');
            if (removeBtn) {
                e.preventDefault();
                this.handleRemoveItem(removeBtn);
            }
        });

        document.addEventListener('change', (e) => {
            if (e.target.matches('.quantity-input')) {
                this.handleQuantityChange(e.target);
            }
        });
    }

    handleAddToCart(button) {
        const productId = button.getAttribute('data-product-id');
        const form = button.closest('form');
        const quantityInput = form && form.querySelector('select[name="quantity"], input[name="quantity"]');
        const quantity = quantityInput ? parseInt(quantityInput.value) : 1;

        this.setButtonLoading(button, true);

        fetch(`/api/cart/add/${productId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quantity }),
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                this.showNotification(data.message || 'Item added to cart!', 'success');
                this.setCartBadge(data.count);
                this.animateAddToCart(button);
            } else {
                this.showNotification(data.error || data.message || 'Unable to add item', 'error');
            }
        })
        .catch(() => this.showNotification('Failed to add item to cart', 'error'))
        .finally(() => this.setButtonLoading(button, false));
    }

    updateQuantity(button, delta) {
        const row = button.closest('tr') || button.closest('.cart-item');
        const input = row && row.querySelector('.quantity-input');
        if (!input) return;
        const newQty = Math.max(0, parseInt(input.value) + delta);
        if (newQty === 0) {
            this.handleRemoveItem(button);
            return;
        }
        input.value = newQty;
        this.handleQuantityChange(input);
    }

    handleQuantityChange(input) {
        const productId = input.getAttribute('data-product-id');
        const quantity = parseInt(input.value);
        if (quantity <= 0) {
            this.handleRemoveItem(input);
            return;
        }
        fetch('/api/cart/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity }),
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                this.setCartBadge(data.count);
                this.updateRowTotal(input.closest('tr') || input.closest('.cart-item'));
                this.updatePageTotal(data.total);
                this.showNotification('Cart updated!', 'success');
            } else {
                this.showNotification(data.error || 'Failed to update cart', 'error');
            }
        })
        .catch(() => this.showNotification('Failed to update cart', 'error'));
    }

    handleRemoveItem(button) {
        if (!confirm('Remove this item from your cart?')) return;
        const productId = button.getAttribute('data-product-id');
        const row = button.closest('tr') || button.closest('.cart-item');
        if (row) { row.style.opacity = '0.5'; row.style.pointerEvents = 'none'; }

        fetch(`/api/cart/remove/${productId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                if (row) row.remove();
                this.setCartBadge(data.count);
                this.updatePageTotal(data.total);
                this.showNotification('Item removed from cart', 'info');
                this.checkEmptyCart();
            } else {
                if (row) { row.style.opacity = '1'; row.style.pointerEvents = 'auto'; }
                this.showNotification(data.error || 'Failed to remove item', 'error');
            }
        })
        .catch(() => {
            if (row) { row.style.opacity = '1'; row.style.pointerEvents = 'auto'; }
            this.showNotification('Failed to remove item', 'error');
        });
    }

    updateRowTotal(row) {
        if (!row) return;
        const input = row.querySelector('.quantity-input');
        const priceEl = row.querySelector('.item-price');
        const totalEl = row.querySelector('.item-total');
        if (input && priceEl && totalEl) {
            const qty = parseInt(input.value);
            const price = parseFloat(priceEl.textContent.replace(/[^\d.]/g, ''));
            totalEl.textContent = `₹${(qty * price).toFixed(2)}`;
        }
    }

    updatePageTotal(total) {
        document.querySelectorAll('.cart-total').forEach(el => {
            el.textContent = `₹${parseFloat(total).toFixed(2)}`;
        });
    }

    updateCartCount() {
        fetch('/api/cart')
            .then(r => r.json())
            .then(data => { if (data.success) this.setCartBadge(data.count); })
            .catch(() => {});
    }

    setCartBadge(count) {
        document.querySelectorAll('.navbar .badge, .cart-badge').forEach(el => {
            el.textContent = count;
            el.style.display = count > 0 ? '' : 'none';
        });
    }

    checkEmptyCart() {
        const items = document.querySelectorAll('.cart-item');
        if (items.length === 0) {
            const container = document.querySelector('.cart-container');
            if (container) {
                container.innerHTML = `
                    <div class="text-center py-5">
                        <i class="fas fa-shopping-cart fa-4x text-muted mb-4"></i>
                        <h3 class="text-muted mb-3">Your cart is empty</h3>
                        <p class="text-muted mb-4">Looks like you haven't added any delicious treats yet.</p>
                        <a href="/products" class="btn btn-brown btn-lg">
                            <i class="fas fa-shopping-bag me-2"></i>Start Shopping
                        </a>
                    </div>`;
            }
        }
    }

    animateAddToCart(button) {
        const orig = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check me-2"></i>Added!';
        button.classList.replace('btn-brown', 'btn-success');
        setTimeout(() => {
            button.innerHTML = orig;
            button.classList.replace('btn-success', 'btn-brown');
        }, 1500);
    }

    setButtonLoading(button, loading) {
        button.disabled = loading;
        if (loading) {
            button._origHTML = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adding...';
        } else if (button._origHTML) {
            button.innerHTML = button._origHTML;
        }
    }

    showNotification(message, type = 'info') {
        const el = document.createElement('div');
        el.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        el.style.cssText = 'top:20px;right:20px;z-index:9999;min-width:300px;';
        el.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
        document.body.appendChild(el);
        setTimeout(() => { if (el.parentNode) el.remove(); }, 3000);
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.cartManager = new CartManager();
});

if (typeof module !== 'undefined' && module.exports) {
    module.exports = CartManager;
}
