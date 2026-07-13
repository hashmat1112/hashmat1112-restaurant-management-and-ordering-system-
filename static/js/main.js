// =============================================
// FoodRush — main.js
// Handles: cart, toast, checkout, payment modal
// =============================================


// ─── CART (stored in localStorage) ───────────

function getCart() {
  return JSON.parse(localStorage.getItem('cart') || '[]');
}

function saveCart(cart) {
  localStorage.setItem('cart', JSON.stringify(cart));
  updateCartCount();
}

function updateCartCount() {
  const cart = getCart();
  const total = cart.reduce((sum, i) => sum + i.qty, 0);
  document.querySelectorAll('#cart-count').forEach(el => el.textContent = total);
}

function addToCart(id, name, price) {
  const cart = getCart();
  const existing = cart.find(i => i.id === id);
  if (existing) {
    existing.qty += 1;
  } else {
    cart.push({ id, name, price: parseFloat(price), qty: 1 });
  }
  saveCart(cart);
  showToast(`${name} added to cart!`);
}


// ─── TOAST NOTIFICATION ──────────────────────

function showToast(msg) {
  const t = document.createElement('div');
  t.textContent = msg;
  t.style.cssText = [
    'position:fixed', 'bottom:2rem', 'right:2rem',
    'background:var(--accent)', 'color:#000',
    'padding:0.8rem 1.4rem', 'border-radius:99px',
    'font-weight:600', 'font-size:0.88rem',
    'z-index:9999', 'animation:slideUp 0.3s ease',
    'box-shadow:0 4px 20px rgba(0,0,0,0.3)'
  ].join(';');
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2500);
}


// ─── CART PAGE ───────────────────────────────

function renderCart() {
  const cart = getCart();
  const empty   = document.getElementById('cart-empty');
  const content = document.getElementById('cart-content');
  if (!empty || !content) return;

  if (cart.length === 0) {
    empty.style.display   = 'block';
    content.style.display = 'none';
    return;
  }

  empty.style.display   = 'none';
  content.style.display = 'block';

  let subtotal = 0;
  const tbody = document.getElementById('cart-body');
  tbody.innerHTML = '';

  cart.forEach((item, i) => {
    subtotal += item.price * item.qty;
    tbody.innerHTML += `
      <tr>
        <td>
          <div class="cart-item-name">${item.name}</div>
        </td>
        <td class="cart-item-price">Rs ${item.price.toFixed(0)}</td>
        <td>
          <div class="qty-control">
            <button class="qty-btn" onclick="changeQty(${i}, -1)">−</button>
            <span>${item.qty}</span>
            <button class="qty-btn" onclick="changeQty(${i}, 1)">+</button>
          </div>
        </td>
        <td style="color:var(--accent);font-weight:600;">Rs ${(item.price * item.qty).toFixed(0)}</td>
        <td>
          <button class="remove-btn" onclick="removeItem(${i})" title="Remove item">🗑</button>
        </td>
      </tr>`;
  });

  const delivery = 50;
  document.getElementById('s-subtotal').textContent = `Rs ${subtotal.toFixed(0)}`;
  document.getElementById('s-total').textContent    = `Rs ${(subtotal + delivery).toFixed(0)}`;
}

function changeQty(index, delta) {
  const cart = getCart();
  cart[index].qty += delta;
  if (cart[index].qty <= 0) cart.splice(index, 1);
  saveCart(cart);
  renderCart();
}

function removeItem(index) {
  const cart = getCart();
  cart.splice(index, 1);
  saveCart(cart);
  renderCart();
}


// ─── CHECKOUT PAGE ───────────────────────────

function selectPay(el, method) {
  document.querySelectorAll('.pay-option').forEach(o => o.classList.remove('selected'));
  el.classList.add('selected');
  const cardFields = document.getElementById('card-fields');
  if (cardFields) {
    cardFields.classList.toggle('visible', method === 'card');
  }
}

function renderSummary() {
  const cart  = getCart();
  const lines = document.getElementById('summary-lines');
  const totalEl = document.getElementById('order-total');
  if (!lines || !totalEl) return;

  let subtotal = 0;
  lines.innerHTML = '';
  cart.forEach(item => {
    subtotal += item.price * item.qty;
    lines.innerHTML += `
      <div class="order-line">
        <span>${item.qty}× ${item.name}</span>
        <span>Rs ${(item.price * item.qty).toFixed(0)}</span>
      </div>`;
  });
  lines.innerHTML += `
    <div class="order-line">
      <span>Delivery fee</span>
      <span>Rs 50</span>
    </div>`;
  totalEl.textContent = `Rs ${(subtotal + 50).toFixed(0)}`;
}

function placeOrder() {
  const cart = getCart();
  if (!cart.length) {
    showToast('Your cart is empty!');
    return;
  }

  const cartInput = document.getElementById('cart-data-input');
  if (cartInput) cartInput.value = JSON.stringify(cart);

  // Show the processing modal
  const modal = document.getElementById('modal');
  if (modal) {
    modal.classList.add('open');
    setTimeout(() => {
      const fill = document.getElementById('proc-fill');
      if (fill) fill.style.width = '100%';
    }, 100);
  }

  // Clear cart and submit after animation
  setTimeout(() => {
    localStorage.removeItem('cart');
    updateCartCount();
    const form = document.getElementById('checkout-form');
    if (form) form.submit();
  }, 2300);
}


// ─── INIT ────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  updateCartCount();
  renderCart();      // runs only if cart page elements exist
  renderSummary();   // runs only if checkout page elements exist
});
