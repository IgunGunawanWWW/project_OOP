/* ============================================
   SLIDER — Absolute Positioning (No Clone)
   Infinite loop tanpa lompatan
   ============================================ */
const sliderContainer = document.querySelector(".slider-container");
const sliderEl = document.querySelector(".slider");
const slides = Array.from(document.querySelectorAll(".slide"));
const total = slides.length;
let current = 0;
let isAnimating = false;

function mod(n, m) {
  return ((n % m) + m) % m;
}

function setupSlider() {
  const slideWidth = sliderContainer.offsetWidth / 3;
  const maxHeight = Math.max(...slides.map((s) => s.scrollHeight)) + 80;

  sliderEl.style.position = "relative";
  sliderEl.style.height = maxHeight + "px";

  slides.forEach((slide) => {
    slide.style.position = "absolute";
    slide.style.width = slideWidth + "px";
    slide.style.top = "0";
    slide.style.left = "0";
    slide.style.padding = "40px 20px";
    slide.style.boxSizing = "border-box";
  });

  positionSlides(false);
}

function positionSlides(animate = true) {
  const slideWidth = sliderContainer.offsetWidth / 3;
  const containerWidth = sliderContainer.offsetWidth;
  const centerX = (containerWidth - slideWidth) / 2;

  slides.forEach((slide, i) => {
    let diff = mod(i - current, total);
    if (diff > Math.floor(total / 2)) diff -= total;

    const x = centerX + diff * slideWidth;
    const isActive = i === current;

    slide.style.transition = animate
      ? "transform 0.6s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.5s ease, filter 0.5s ease"
      : "none";

    slide.style.transform = `translateX(${x}px) scale(${isActive ? 1.15 : 0.8})`;
    slide.style.opacity = isActive ? "1" : "0.2";
    slide.style.filter = isActive ? "blur(0)" : "blur(4px)";
    slide.style.zIndex = isActive ? "10" : "1";
    slide.classList.toggle("active", isActive);
  });
}

function nextSlide() {
  if (isAnimating) return;
  isAnimating = true;
  current = mod(current + 1, total);
  positionSlides(true);
  setTimeout(() => {
    isAnimating = false;
  }, 650);
}

function prevSlide() {
  if (isAnimating) return;
  isAnimating = true;
  current = mod(current - 1, total);
  positionSlides(true);
  setTimeout(() => {
    isAnimating = false;
  }, 650);
}

window.addEventListener("load", setupSlider);
window.addEventListener("resize", () => setupSlider());

/* ============================================
   DETAIL SLIDER
   ============================================ */
function openDetailFromEl(el) {
  document.getElementById("detail-title").innerText = el.dataset.title;
  document.getElementById("detail-price").innerText = el.dataset.price;
  document.getElementById("detail-desc").innerText = el.dataset.desc;
  document.getElementById("detail-img").src = el.dataset.img;
  document.getElementById("product-detail").dataset.menuId = el.dataset.id;
  document.getElementById("product-detail").style.display = "flex";
  document.body.style.overflow = "hidden";
}

function closeDetail() {
  document.getElementById("product-detail").style.display = "none";
  document.body.style.overflow = "auto";
}

function addFromSlider() {
  const menuId = document.getElementById("product-detail").dataset.menuId;
  fetch("/cart/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ menu_id: menuId, jumlah: 1 }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "ok") {
        const cartCount = document.getElementById("cart-count");
        cartCount.innerText = parseInt(cartCount.innerText) + 1;
        closeDetail();
      }
    });
}

/* ============================================
   CART
   ============================================ */
function toggleCart() {
  const modal = document.getElementById("cart-page");
  const isOpen = modal.style.display === "flex";
  if (isOpen) {
    modal.style.display = "none";
  } else {
    modal.style.display = "flex";
    loadCart();
  }
}

function loadCart() {
  fetch("/cart")
    .then((res) => res.json())
    .then((data) => {
      const emptyDiv = document.getElementById("empty-cart");
      const filledDiv = document.getElementById("filled-cart");
      const itemList = document.querySelector(".cart-item-list");
      const cartCount = document.getElementById("cart-count");

      if (data.items.length === 0) {
        emptyDiv.style.display = "block";
        filledDiv.style.display = "none";
        cartCount.innerText = "0";
        return;
      }

      emptyDiv.style.display = "none";
      filledDiv.style.display = "block";
      cartCount.innerText = data.items.length;

      itemList.innerHTML = "";
      data.items.forEach((item) => {
        itemList.innerHTML += `
                    <div class="cart-item">
                        <span class="cart-item-name">${item.nama_kopi} x${item.jumlah}</span>
                        <div class="cart-item-right">
                            <span class="cart-item-price">Rp ${Number(item.subtotal).toLocaleString("id-ID")}</span>
                            <button class="remove-btn" onclick="removeFromCart('${item.nama_kopi}')">✕</button>
                        </div>
                    </div>
                `;
      });

      const delivery = 10000;
      document.getElementById("sub-total").innerText =
        "Rp " + Number(data.total).toLocaleString("id-ID");
      document.getElementById("grand-total").innerText =
        "Rp " + Number(data.total + delivery).toLocaleString("id-ID");
    });
}

function addToCart(itemName, price) {
  fetch("/cart/add-by-name", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nama: itemName, harga: price, jumlah: 1 }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "ok") {
        const cartCount = document.getElementById("cart-count");
        cartCount.innerText = parseInt(cartCount.innerText) + 1;
      }
    });
}

function removeFromCart(itemName) {
  fetch("/cart/remove", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nama: itemName }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "ok") loadCart();
    });
}

function checkout() {
  fetch("/cart/checkout", { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "ok") {
        document.getElementById("cart-page").style.display = "none";
        document.getElementById("checkout-success").style.display = "flex";
        document.getElementById("cart-count").innerText = "0";
      }
    });
}

function closeCheckout() {
  document.getElementById("checkout-success").style.display = "none";
}

/* ============================================
   CARD DETAIL MODAL
   ============================================ */
let cardDetailItem = { name: "", price: 0, img: "" };

function openCardDetail(name, price, img) {
  cardDetailItem = { name, price, img };
  document.getElementById("card-detail-name").innerText = name;
  document.getElementById("card-detail-price-display").innerText =
    "Rp " + price.toLocaleString("id-ID");
  document.getElementById("card-detail-img").src = img;
  document.getElementById("card-detail-qty").innerText = 1;
  document.getElementById("card-detail-modal").style.display = "flex";
  document.body.style.overflow = "hidden";
}

function closeCardDetail() {
  document.getElementById("card-detail-modal").style.display = "none";
  document.body.style.overflow = "auto";
}

function changeQty(delta) {
  const qtyEl = document.getElementById("card-detail-qty");
  let qty = parseInt(qtyEl.innerText) + delta;
  if (qty < 1) qty = 1;
  qtyEl.innerText = qty;
}

function addFromCardDetail() {
  const qty = parseInt(document.getElementById("card-detail-qty").innerText);
  fetch("/cart/add-by-name", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      nama: cardDetailItem.name,
      harga: cardDetailItem.price,
      jumlah: qty,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "ok") {
        const cartCount = document.getElementById("cart-count");
        cartCount.innerText = parseInt(cartCount.innerText) + qty;
        closeCardDetail();
      }
    });
}
