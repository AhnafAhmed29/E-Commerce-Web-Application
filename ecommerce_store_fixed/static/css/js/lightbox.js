/* ========================================
   IMAGE ZOOM / LIGHTBOX – FIXED VERSION
   Fixes: Image replacement bug, proper alignment
   ======================================== */

let currentImageIndex = 0;
let productImages = [];

/* ---- Bootstrap ---- */
function initLightbox() {
    productImages = [];
    createLightboxElement();

    const mainImg = document.getElementById('main-product-img');

    if (!mainImg) return; // not on a product detail page – nothing to do

    // Collect images
    productImages.push(mainImg.src);
    document.querySelectorAll('.product-thumb').forEach(function(t) {
        if (!productImages.includes(t.src)) productImages.push(t.src);
    });

    // Hover zoom on main image
    mainImg.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.08)';
    });
    mainImg.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
    });

    // Click main image → open lightbox
    mainImg.addEventListener('click', function() {
        currentImageIndex = 0;
        openLightbox(this.src);
    });

    // Thumbnail clicks → ONLY open lightbox (DON'T change main image)
    // FIX: Removed the line that permanently changed main image
    document.querySelectorAll('.product-thumb').forEach(function(thumb) {
        // highlight wrapper on hover
        var wrap = thumb.closest('.product-thumb-wrap');
        if (wrap) {
            thumb.addEventListener('mouseenter', function() {
                wrap.style.borderColor = '#f4d03f';
            });
            thumb.addEventListener('mouseleave', function() {
                wrap.style.borderColor = 'transparent';
            });
        }

        thumb.addEventListener('click', function() {
            // FIX: DON'T change main image - just open lightbox with selected image
            // Old buggy line removed: if (mainImg) mainImg.src = this.src;
            currentImageIndex = productImages.indexOf(this.src);
            if (currentImageIndex === -1) currentImageIndex = 0;
            openLightbox(this.src);
        });
    });

    // Update counter
    var totalEl = document.getElementById('total-images');
    if (totalEl) totalEl.textContent = productImages.length;
}

/* ---- Build DOM ---- */
function createLightboxElement() {
    if (document.getElementById('image-lightbox')) return;

    var lb = document.createElement('div');
    lb.id = 'image-lightbox';
    lb.className = 'lightbox';
    lb.innerHTML =
        '<span class="close-lightbox" onclick="closeLightbox()">&times;</span>' +
        '<img id="lightbox-image" src="" alt="Product Image">' +
        '<div class="lightbox-controls">' +
            '<button onclick="changeImage(-1); event.stopPropagation();">&#10094; Prev</button>' +
            '<button onclick="changeImage(1);  event.stopPropagation();">Next &#10095;</button>' +
        '</div>' +
        '<div class="image-counter">' +
            '<span id="current-image-num">1</span> / <span id="total-images">1</span>' +
        '</div>';

    lb.addEventListener('click', function(e) {
        if (e.target === lb) closeLightbox();
    });

    document.body.appendChild(lb);
}

/* ---- Open / Close ---- */
function openLightbox(src) {
    var lb  = document.getElementById('image-lightbox');
    var img = document.getElementById('lightbox-image');
    if (!lb || !img) return;
    img.src = src;
    lb.classList.add('active');
    document.body.style.overflow = 'hidden';
    updateImageCounter();
}

function closeLightbox() {
    var lb = document.getElementById('image-lightbox');
    if (lb) lb.classList.remove('active');
    document.body.style.overflow = '';
    // Main image stays as it was - no restoration needed since we don't change it
}

/* ---- Navigate ---- */
function changeImage(dir) {
    if (!productImages.length) return;
    currentImageIndex = (currentImageIndex + dir + productImages.length) % productImages.length;
    var img = document.getElementById('lightbox-image');
    if (img) img.src = productImages[currentImageIndex];
    updateImageCounter();
}

function updateImageCounter() {
    var cur = document.getElementById('current-image-num');
    var tot = document.getElementById('total-images');
    if (cur) cur.textContent = currentImageIndex + 1;
    if (tot) tot.textContent = productImages.length;
}

/* ---- Keyboard ---- */
document.addEventListener('keydown', function(e) {
    var lb = document.getElementById('image-lightbox');
    if (!lb || !lb.classList.contains('active')) return;
    if (e.key === 'Escape')     closeLightbox();
    if (e.key === 'ArrowLeft')  changeImage(-1);
    if (e.key === 'ArrowRight') changeImage(1);
});

/* ---- Touch / Swipe ---- */
var _touchStartX = 0;
document.addEventListener('touchstart', function(e) {
    if (document.getElementById('image-lightbox') &&
        document.getElementById('image-lightbox').classList.contains('active')) {
        _touchStartX = e.changedTouches[0].screenX;
    }
});
document.addEventListener('touchend', function(e) {
    var lb = document.getElementById('image-lightbox');
    if (!lb || !lb.classList.contains('active')) return;
    var diff = e.changedTouches[0].screenX - _touchStartX;
    if (Math.abs(diff) > 50) changeImage(diff < 0 ? 1 : -1);
});

/* ---- Init ---- */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLightbox);
} else {
    initLightbox();
}

window.openLightbox  = openLightbox;
window.closeLightbox = closeLightbox;
window.changeImage   = changeImage;