
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
    modal.style.display = (modal.style.display === 'flex') ? 'none' : 'flex';
    updateCartUI();
}

// Fungsi simulasi tambah pesanan (Panggil fungsi ini saat klik "Add to cart")
function addToCart(itemName, price) {
    cart.push({ name: itemName, price: price });
    document.getElementById('cart-count').innerText = cart.length;
    alert(itemName + " ditambahkan ke keranjang!");
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
        document.getElementById('sub-total').innerText = 'RP ' + (total/1000) + 'K';
        document.getElementById('grand-total').innerText = 'RP ' + ((total + 10000)/1000) + 'K';
    }
}
// End cart
