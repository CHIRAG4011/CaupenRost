/**
 * CaupenRost - Cart Management
 * Handles shopping cart functionality and interactions
 */

class CartManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateCartDisplay();
    }

    bindEvents() {
        // Add to cart buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.add-to-cart-btn') || e.target.closest('.add-to-cart-btn')) {
                e.preventDefault();
                this.handleAddToCart(e.target.closest('.add-to-cart-btn') || e.target);
            }
        });

        // Quantity update buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.quantity-minus')) {
                e.preventDefault();
                this.updateQuantity(e.target, -1);
            } else if (e.target.matches('.quantity-plus')) {
                e.preventDefault();
                this.updateQuantity(e.target, 1);
            }
        });

        // Remove item buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.remove-item-btn') || e.target.closest('.remove-item-btn')) {
                e.preventDefault();
                this.handleRemoveItem(e.target.closest('.remove-item-btn') || e.target);
            }
        });

        // Quantity input changes
        document.addEventListener('change', (e) => {
            if (e.target.matches('.quantity-input')) {
                this.handleQuantityChange(e.target);
            }
        });
    }

    handleAddToCart(button) {
        const productId = button.getAttribute('data-product-id') || 
                         button.closest('form')?.action?.split('/').pop();
        const form = button.closest('form');
        const quantityInput = form?.querySelector('select[name="quantity"], input[name="quantity"]');
        const quantity = quantityInput ? quantityInput.value : 1;

        // Show loading state
        this.setButtonLoading(button, true);

        // Create form data
        const formData = new FormData();
        formData.append('quantity', quantity);

        fetch(`/add_to_cart/${productId}`, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                return response.text();
            }
            throw new Error('Failed to add item to cart');
        })
        .then(html => {
            // Check if response contains success message
            if (html.includes('added to cart') || html.includes('success')) {
                this.showCartNotification('Item added to cart!', 'success');
                this.updateCartDisplay();
                this.animateAddToCart(button);
            } else {
                this.showCartNotification('Unable to add item to cart', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showCartNotification('Failed to add item to cart', 'error');
        })
        .finally(() => {
            this.setButtonLoading(button, false);
        });
    }

    updateQuantity(button, delta) {
        const row = button.closest('tr') || button.closest('.cart-item');
        const quantityInput = row.querySelector('.quantity-input');
        const currentQuantity = parseInt(quantityInput.value);
        const newQuantity = Math.max(0, currentQuantity + delta);
        
        if (newQuantity === 0) {
            this.handleRemoveItem(button);
            return;
        }

        quantityInput.value = newQuantity;
        this.handleQuantityChange(quantityInput);
    }

    handleQuantityChange(input) {
        const productId = input.getAttribute('data-product-id');
        const quantity = parseInt(input.value);
        const row = input.closest('tr') || input.closest('.cart-item');

        if (quantity <= 0) {
            this.handleRemoveItem(input);
            return;
        }

        // Update quantity via form submission
        const form = input.closest('form');
        if (form) {
            const formData = new FormData(form);
            
            fetch('/update_cart', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    this.updateCartDisplay();
                    this.updateRowTotal(row);
                    this.showCartNotification('Cart updated!', 'success');
                } else {
                    throw new Error('Failed to update cart');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.showCartNotification('Failed to update cart', 'error');
            });
        }
    }

    handleRemoveItem(button) {
        if (confirm('Remove this item from your cart?')) {
            const productId = button.getAttribute('data-product-id');
            const row = button.closest('tr') || button.closest('.cart-item');
            
            // Animate removal
            row.style.opacity = '0.5';
            row.style.pointerEvents = 'none';

            fetch(`/remove_from_cart/${productId}`)
            .then(response => {
                if (response.ok) {
                    row.remove();
                    this.updateCartDisplay();
                    this.showCartNotification('Item removed from cart', 'info');
                    this.checkEmptyCart();
                } else {
                    throw new Error('Failed to remove item');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.showCartNotification('Failed to remove item', 'error');
                // Restore row state
                row.style.opacity = '1';
                row.style.pointerEvents = 'auto';
            });
        }
    }

    updateRowTotal(row) {
        const quantityInput = row.querySelector('.quantity-input');
        const priceElement = row.querySelector('.item-price');
        const totalElement = row.querySelector('.item-total');
        
        if (quantityInput && priceElement && totalElement) {
            const quantity = parseInt(quantityInput.value);
            const price = parseFloat(priceElement.textContent.replace('₹', ''));
            const total = quantity * price;
            
            totalElement.textContent = `₹${total.toFixed(2)}`;
        }
    }

    updateCartDisplay() {
        // This would typically fetch updated cart data from the server
        // For now, we'll update the cart count in the navbar
        this.updateCartCount();
        this.updateCartTotal();
    }

    updateCartCount() {
        fetch('/cart')
        .then(response => response.text())
        .then(html => {
            // Parse the response to extract cart count
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const cartBadge = document.querySelector('.navbar .badge');
            const newCartBadge = doc.querySelector('.navbar .badge');
            
            if (cartBadge && newCartBadge) {
                cartBadge.textContent = newCartBadge.textContent;
                cartBadge.style.display = newCartBadge.style.display;
            }
        })
        .catch(error => console.error('Error updating cart count:', error));
    }

    updateCartTotal() {
        const cartTotalElements = document.querySelectorAll('.cart-total');
        if (cartTotalElements.length === 0) return;

        // Calculate total from visible items
        let total = 0;
        document.querySelectorAll('.item-total').forEach(element => {
            const value = parseFloat(element.textContent.replace('₹', ''));
            total += value;
        });

        cartTotalElements.forEach(element => {
            element.textContent = `₹${total.toFixed(2)}`;
        });
    }

    checkEmptyCart() {
        const cartItems = document.querySelectorAll('.cart-item');
        if (cartItems.length === 0) {
            // Show empty cart message
            const cartContainer = document.querySelector('.cart-container');
            if (cartContainer) {
                cartContainer.innerHTML = `
                    <div class="text-center py-5">
                        <i class="fas fa-shopping-cart fa-4x text-muted mb-4"></i>
                        <h3 class="text-muted mb-3">Your cart is empty</h3>
                        <p class="text-muted mb-4">Looks like you haven't added any delicious treats to your cart yet.</p>
                        <a href="/products" class="btn btn-brown btn-lg">
                            <i class="fas fa-shopping-bag me-2"></i>Start Shopping
                        </a>
                    </div>
                `;
            }
        }
    }

    animateAddToCart(button) {
        // Create a small animation effect
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check me-2"></i>Added!';
        button.classList.add('btn-success');
        button.classList.remove('btn-brown');

        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('btn-success');
            button.classList.add('btn-brown');
        }, 1500);
    }

    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adding...';
        } else {
            button.disabled = false;
        }
    }

    showCartNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    // Utility method for formatting currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    }
}

// Initialize cart manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.cartManager = new CartManager();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CartManager;
}
