// Inisialisasi variabel global
const slider = document.querySelector('.slider');
const sliderContainer = document.querySelector('.slider-container');
const slidesOriginal = document.querySelectorAll('.slide');
const totalOriginal = slidesOriginal.length;

// 1. PROSES CLONING (Untuk Looping)
const lastClone = slidesOriginal[totalOriginal - 1].cloneNode(true);
const firstClone = slidesOriginal[0].cloneNode(true);
slider.insertAdjacentElement('afterbegin', lastClone);
slider.insertAdjacentElement('beforeend', firstClone);

// Ambil semua slide setelah clone ditambah
let allSlides = document.querySelectorAll('.slide');
let current = 1; // Mulai dari item asli pertama

function updateSlider(isInstant = false) {
    if (isInstant) {
        slider.style.transition = 'none';
    } else {
        slider.style.transition = 'all 0.6s cubic-bezier(0.22, 1, 0.36, 1)';
    }

    // Hitung posisi dinamis (PENTING UNTUK HP & LAPTOP)
    const slideWidth = allSlides[0].offsetWidth;
    const containerWidth = sliderContainer.offsetWidth;
    const centerOffset = (containerWidth - slideWidth) / 2;
    const totalOffset = -(current * slideWidth) + centerOffset;

    slider.style.transform = `translateX(${totalOffset}px)`;

    // Update Class Active (Ini yang memperbaiki tampilan blur)
    allSlides.forEach((slide, index) => {
        slide.classList.remove('active');
        if (index === current) {
            slide.classList.add('active');
        }
    });
}

// Navigasi
function nextSlide() {
    if (current >= allSlides.length - 1) return;
    current++;
    updateSlider();
}

function prevSlide() {
    if (current <= 0) return;
    current--;
    updateSlider();
}

// Handler Looping Instan
slider.addEventListener('transitionend', () => {
    if (allSlides[current].innerHTML === firstClone.innerHTML) {
        current = 1;
        updateSlider(true);
    }
    if (allSlides[current].innerHTML === lastClone.innerHTML) {
        current = totalOriginal;
        updateSlider(true);
    }
});

// Jalankan saat load dan saat resize layar
window.addEventListener('load', () => updateSlider(true));
window.addEventListener('resize', () => updateSlider(true));

/* --- FUNGSI DETAIL --- */
function openDetail(title, price, desc, img) {
    document.getElementById('detail-title').innerText = title;
    document.getElementById('detail-price').innerText = price;
    document.getElementById('detail-desc').innerText = desc;
    document.getElementById('detail-img').src = img;
    document.getElementById('product-detail').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeDetail() {
    document.getElementById('product-detail').style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Cart
let cart = []; // Array untuk menyimpan pesanan

function toggleCart() {
    const modal = document.getElementById('cart-page');
    modal.style.display = modal.style.display === 'flex' ? 'none' : 'flex';
    updateCartUI();
}

// Fungsi simulasi tambah pesanan (Panggil fungsi ini saat klik "Add to cart")
function addToCart(itemName, price) {
    fetch('/cart/add-by-name', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nama: itemName, harga: price, jumlah: 1 }),
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.status === 'ok') {
                const cartCount = document.getElementById('cart-count');
                cartCount.innerText = parseInt(cartCount.innerText) + 1;
            }
        });
}

function updateCartUI() {
    const emptyDiv = document.getElementById('empty-cart');
    const filledDiv = document.getElementById('filled-cart');

    if (cart.length === 0) {
        emptyDiv.style.display = 'block';
        filledDiv.style.display = 'none';
    } else {
        emptyDiv.style.display = 'none';
        filledDiv.style.display = 'block';

        // Update Ringkasan Harga (Contoh sederhana)
        let total = cart.reduce((sum, item) => sum + item.price, 0);
        document.getElementById('sub-total').innerText =
            'RP ' + total / 1000 + 'K';
        document.getElementById('grand-total').innerText =
            'RP ' + (total + 10000) / 1000 + 'K';
    }
}
// End cart

// ganti slide di awal
function openDetailFromEl(el) {
    document.getElementById('detail-title').innerText = el.dataset.title;
    document.getElementById('detail-price').innerText = el.dataset.price;
    document.getElementById('detail-desc').innerText = el.dataset.desc;
    document.getElementById('detail-img').src = el.dataset.img;
    document.getElementById('product-detail').dataset.menuId = el.dataset.id;
    document.getElementById('product-detail').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function toggleCart() {
    const modal = document.getElementById('cart-page');
    const isOpen = modal.style.display === 'flex';

    if (isOpen) {
        modal.style.display = 'none';
    } else {
        modal.style.display = 'flex';
        loadCart();
    }
}

function loadCart() {
    fetch('/cart')
        .then((res) => res.json())
        .then((data) => {
            const emptyDiv = document.getElementById('empty-cart');
            const filledDiv = document.getElementById('filled-cart');
            const itemList = document.querySelector('.cart-item-list');
            const cartCount = document.getElementById('cart-count');

            if (data.items.length === 0) {
                emptyDiv.style.display = 'block';
                filledDiv.style.display = 'none';
                cartCount.innerText = '0';
                return;
            }

            emptyDiv.style.display = 'none';
            filledDiv.style.display = 'block';
            cartCount.innerText = data.items.length;

            itemList.innerHTML = '';
            data.items.forEach((item) => {
                itemList.innerHTML += `
                    <div class="cart-item">
                        <span class="cart-item-name">${item.nama_kopi} x${item.jumlah}</span>
                        <div class="cart-item-right">
                            <span class="cart-item-price">Rp ${Number(item.subtotal).toLocaleString('id-ID')}</span>
                            <button class="remove-btn" onclick="removeFromCart('${item.nama_kopi}')">✕</button>
                        </div>
                    </div>
                `;
            });

            const delivery = 10000;
            document.getElementById('sub-total').innerText =
                'Rp ' + Number(data.total).toLocaleString('id-ID');
            document.getElementById('grand-total').innerText =
                'Rp ' + Number(data.total + delivery).toLocaleString('id-ID');
        });
}

let cardDetailItem = { name: '', price: 0, img: '' };
function openCardDetail(name, price, img) {
    cardDetailItem = { name, price, img };
    document.getElementById('card-detail-name').innerText = name;
    document.getElementById('card-detail-price-display').innerText =
        'Rp ' + price.toLocaleString('id-ID');
    document.getElementById('card-detail-img').src = img;
    document.getElementById('card-detail-qty').innerText = 1;
    document.getElementById('card-detail-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeCardDetail() {
    document.getElementById('card-detail-modal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

function changeQty(delta) {
    const qtyEl = document.getElementById('card-detail-qty');
    let qty = parseInt(qtyEl.innerText) + delta;
    if (qty < 1) qty = 1;
    qtyEl.innerText = qty;
}

function addFromCardDetail() {
    const qty = parseInt(document.getElementById('card-detail-qty').innerText);
    fetch('/cart/add-by-name', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            nama: cardDetailItem.name,
            harga: cardDetailItem.price,
            jumlah: qty,
        }),
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.status === 'ok') {
                const cartCount = document.getElementById('cart-count');
                cartCount.innerText = parseInt(cartCount.innerText) + qty;
                closeCardDetail();
            }
        });
}

function removeFromCart(itemName) {
    fetch('/cart/remove', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nama: itemName }),
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.status === 'ok') loadCart();
        });
}

function addFromSlider() {
    const menuId = document.getElementById('product-detail').dataset.menuId;
    fetch('/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ menu_id: menuId, jumlah: 1 }),
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.status === 'ok') {
                const cartCount = document.getElementById('cart-count');
                cartCount.innerText = parseInt(cartCount.innerText) + 1;
                closeDetail();
            }
        });
}

function checkout() {
    fetch('/cart/checkout', { method: 'POST' })
        .then((res) => res.json())
        .then((data) => {
            if (data.status === 'ok') {
                document.getElementById('cart-page').style.display = 'none';
                document.getElementById('checkout-success').style.display =
                    'flex';
                document.getElementById('cart-count').innerText = '0';
            }
        });
}

function closeCheckout() {
    document.getElementById('checkout-success').style.display = 'none';
}
