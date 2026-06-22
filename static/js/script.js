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

    slide.style.transform = `translateX(${x}px) scale(${isActive ? 1.12 : 0.85})`;
    slide.style.opacity = isActive ? "1" : "0.35";
    slide.style.filter = isActive ? "blur(0)" : "blur(2px)";
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
  document.getElementById("detail-qty").innerText = 1;
  document.getElementById("product-detail").dataset.menuId = el.dataset.id;
  document.getElementById("product-detail").style.display = "flex";
  document.body.style.overflow = "hidden";
}

function changeDetailQty(delta) {
  const qtyEl = document.getElementById("detail-qty");
  let qty = parseInt(qtyEl.innerText) + delta;
  if (qty < 1) qty = 1;
  qtyEl.innerText = qty;
}

function closeDetail() {
  document.getElementById("product-detail").style.display = "none";
  document.body.style.overflow = "auto";
}

function addFromSlider() {
  const menuId = document.getElementById("product-detail").dataset.menuId;
  const qty = parseInt(document.getElementById("detail-qty").innerText);
  fetch("/cart/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ menu_id: menuId, jumlah: qty }),
  })
    .then((res) => res.json())
    .then((data) => {
      handleAddResult(data, qty);
      if (["ok", "busy", "habis"].includes(data.status)) closeDetail();
    });
}

/* ============================================
   CART & STATUS PESANAN
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

/* Tampilkan satu panel di dalam modal cart, sembunyikan sisanya */
function showCartPanel(id) {
  ["empty-cart", "filled-cart", "order-status", "order-done"].forEach((p) => {
    document.getElementById(p).style.display = p === id ? "block" : "none";
  });
}

function renderCartItems(container, items, editable) {
  document.querySelector(container).innerHTML = items
    .map((item) => {
      const nama = escapeAttr(item.nama_kopi);
      const src = resolveImg(item.gambar);
      const thumb = src
        ? `<img src="${src}" alt="${item.nama_kopi}" loading="lazy" onerror="this.parentNode.innerHTML='&lt;i class=&quot;fas fa-mug-hot&quot;&gt;&lt;/i&gt;'" />`
        : `<i class="fas fa-mug-hot"></i>`;
      const kategori = item.kategori
        ? `<span class="cart-item-tag">${item.kategori}</span>`
        : "";
      const harga = `Rp ${Number(item.harga_satuan ?? item.subtotal).toLocaleString("id-ID")}`;
      const subtotal = `Rp ${Number(item.subtotal).toLocaleString("id-ID")}`;

      const controls = editable
        ? `<div class="cart-item-actions">
              <div class="qty-selector cart-qty">
                  <button onclick="updateCartQty('${nama}', ${item.jumlah - 1})">−</button>
                  <span>${item.jumlah}</span>
                  <button onclick="updateCartQty('${nama}', ${item.jumlah + 1})">+</button>
              </div>
              <button class="remove-btn" onclick="removeFromCart('${nama}')">✕</button>
           </div>`
        : `<span class="cart-item-qty">x${item.jumlah}</span>`;

      return `
        <div class="cart-item">
            <div class="cart-item-thumb">${thumb}</div>
            <div class="cart-item-info">
                ${kategori}
                <span class="cart-item-name">${item.nama_kopi}</span>
                <span class="cart-item-unit">${harga}</span>
            </div>
            <div class="cart-item-right">
                <span class="cart-item-price">${subtotal}</span>
                ${controls}
            </div>
        </div>`;
    })
    .join("");
}

/* Escape tanda kutip supaya nama menu aman dipakai di atribut onclick */
function escapeAttr(str) {
  return String(str).replace(/'/g, "\\'").replace(/"/g, "&quot;");
}

/* Lengkapi path gambar: data lama disimpan tanpa prefix /static/ */
function resolveImg(gambar) {
  if (!gambar) return "";
  const g = String(gambar).trim();
  if (!g) return "";
  if (/^https?:\/\//.test(g) || g.startsWith("/")) return g;
  return "/static/" + g.replace(/^\/+/, "");
}

/* Ubah kuantitas item langsung dari keranjang */
function updateCartQty(nama, jumlahBaru) {
  if (jumlahBaru < 1) return; // hapus item lewat tombol ✕, bukan tombol −
  fetch("/cart/update-qty", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nama: nama, jumlah: jumlahBaru }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "ok") {
        loadCart();
      } else if (data.status === "habis" || data.status === "busy") {
        showToast(data.message);
      }
    });
}

/* Badge keranjang = total kuantitas item */
function setCartCount(items) {
  const total = items.reduce((sum, it) => sum + it.jumlah, 0);
  document.getElementById("cart-count").innerText = total;
}

function loadCart() {
  fetch("/cart")
    .then((res) => res.json())
    .then((data) => {
      if (data.status !== "ok") {
        document.getElementById("cart-count").innerText = "0";
        return;
      }

      if (data.mode === "cart") {
        showCartPanel("filled-cart");
        setCartWide(true);
        renderCartItems(".cart-item-list", data.items, true);
        const total = "Rp " + Number(data.total).toLocaleString("id-ID");
        const totalQty = data.items.reduce((sum, it) => sum + it.jumlah, 0);
        document.getElementById("total-items").innerText = totalQty;
        document.getElementById("sub-total").innerText = total;
        document.getElementById("final-payment").innerText = total;
        document.getElementById("cart-items-count").innerText =
          data.items.length + " item";
        setCartCount(data.items);
      } else if (data.mode === "diproses") {
        showCartPanel("order-status");
        setCartWide(false);
        renderCartItems("#order-item-list", data.items, false);
        document.getElementById("order-total").innerText =
          "Rp " + Number(data.total).toLocaleString("id-ID");
        setCartCount(data.items);
      } else if (data.mode === "selesai" || data.mode === "dibatalkan") {
        showCartPanel("order-done");
        setCartWide(false);
        renderOrderDone(data.mode);
        document.getElementById("cart-count").innerText = "0";
      } else {
        showCartPanel("empty-cart");
        setCartWide(false);
        document.getElementById("cart-count").innerText = "0";
      }
    });
}

/* Lebarkan modal hanya saat menampilkan isi keranjang (layout 2 kolom) */
function setCartWide(wide) {
  document
    .querySelector("#cart-page .cart-content")
    .classList.toggle("wide", wide);
}

function renderOrderDone(mode) {
  const icon = document.getElementById("order-done-icon");
  const title = document.getElementById("order-done-title");
  const text = document.getElementById("order-done-text");
  if (mode === "dibatalkan") {
    icon.className = "order-done-icon cancelled";
    icon.innerHTML = '<i class="fas fa-xmark"></i>';
    title.innerText = "Pesanan Dibatalkan";
    text.innerText =
      "Pesananmu sudah dibatalkan. Yuk pesan lagi menu favoritmu.";
  } else {
    icon.className = "order-done-icon";
    icon.innerHTML = '<i class="fas fa-check"></i>';
    title.innerText = "Pesanan Sudah Diterima";
    text.innerText =
      "Terima kasih! Pesananmu sudah selesai. Yuk pesan menu selanjutnya.";
  }
}

/* Hasil penambahan item: ok -> tambah badge, busy -> notifikasi */
function handleAddResult(data, qty) {
  if (data.status === "ok") {
    const cartCount = document.getElementById("cart-count");
    cartCount.innerText = parseInt(cartCount.innerText || "0") + qty;
  } else if (data.status === "busy" || data.status === "habis") {
    showToast(data.message);
  }
}

function addToCart(btn, itemName, price) {
  // Ambil gambar dari kartu menu supaya bisa ditampilkan & disimpan di keranjang
  let gambar = "";
  const card = btn && btn.closest ? btn.closest(".coffee-card") : null;
  const img = card ? card.querySelector(".card-image img") : null;
  if (img) gambar = img.getAttribute("src");

  fetch("/cart/add-by-name", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nama: itemName, harga: price, jumlah: 1, gambar }),
  })
    .then((res) => res.json())
    .then((data) => handleAddResult(data, 1));
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
      }
    });
}

function closeCheckout() {
  document.getElementById("checkout-success").style.display = "none";
  loadCart();
}

/* Batalkan pesanan yang sedang diproses */
function cancelOrder() {
  if (!confirm("Yakin mau membatalkan pesanan ini?")) return;
  fetch("/cart/cancel", { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "ok") {
        loadCart();
      } else {
        showToast(data.message || "Gagal membatalkan pesanan.");
      }
    });
}

/* "Pesan Lagi" — tutup notifikasi pesanan selesai, lalu tutup modal */
function orderAgain() {
  fetch("/cart/ack", { method: "POST" }).finally(() => toggleCart());
}

/* Toast kecil untuk notifikasi singkat */
function showToast(message) {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.innerText = message;
  toast.classList.add("show");
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove("show"), 2800);
}

/* Sinkronkan badge keranjang saat halaman dibuka */
window.addEventListener("load", loadCart);

/* ============================================
   CARD DETAIL MODAL
   ============================================ */
let cardDetailItem = { name: "", price: 0, img: "" };

function openCardDetail(name, price, img) {
  cardDetailItem = { name, price, img };
  document.getElementById("card-detail-name").innerText = name;
  document.getElementById("card-detail-price-display").innerText =
    "Rp " + price.toLocaleString("id-ID");
  const imgEl = document.getElementById("card-detail-img");
  if (img) {
    imgEl.src = img;
    imgEl.style.display = "";
  } else {
    imgEl.removeAttribute("src");
    imgEl.style.display = "none";
  }
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
      gambar: cardDetailItem.img,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      handleAddResult(data, qty);
      if (["ok", "busy", "habis"].includes(data.status)) closeCardDetail();
    });
}
