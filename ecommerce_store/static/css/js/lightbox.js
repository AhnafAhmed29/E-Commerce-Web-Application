/* ========================================
   IMAGE ZOOM / LIGHTBOX JAVASCRIPT
   ======================================== */

// Global variables
let currentImageIndex = 0;
let productImages = [];

// Initialize lightbox
function initLightbox() {
    // Collect all product images
    productImages = [];
    
    // Get main image
    const mainImage = document.querySelector('.product-image img');
    if (mainImage && mainImage.src) {
        productImages.push(mainImage.src);
    }
    
    // Get thumbnail images
    const thumbnails = document.querySelectorAll('.thumbnail-images img');
    thumbnails.forEach(thumb => {
        if (thumb.src && !productImages.includes(thumb.src)) {
            productImages.push(thumb.src);
        }
    });
    
    // Add click handlers to all product images
    addClickHandlers();
    
    // Create lightbox if it doesn't exist
    createLightboxElement();
}

// Add click handlers to images
function addClickHandlers() {
    // Main product image
    const mainImage = document.querySelector('.product-image img');
    if (mainImage) {
        mainImage.addEventListener('click', function() {
            currentImageIndex = 0;
            openLightbox(this.src);
        });
    }
    
    // Thumbnail images
    const thumbnails = document.querySelectorAll('.thumbnail-images img');
    thumbnails.forEach((thumb, index) => {
        thumb.addEventListener('click', function() {
            currentImageIndex = index;
            openLightbox(this.src);
        });
    });
}

// Create lightbox HTML element
function createLightboxElement() {
    // Check if lightbox already exists
    if (document.getElementById('image-lightbox')) return;
    
    const lightbox = document.createElement('div');
    lightbox.id = 'image-lightbox';
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <span class="close-lightbox" onclick="closeLightbox()">&times;</span>
        <img id="lightbox-image" src="" alt="Product Image">
        <div class="lightbox-controls">
            <button onclick="changeImage(-1); event.stopPropagation();">❮ Prev</button>
            <button onclick="changeImage(1); event.stopPropagation();">Next ❯</button>
        </div>
        <div class="image-counter">
            <span id="current-image-num">1</span> / <span id="total-images">${productImages.length}</span>
        </div>
    `;
    
    // Click outside to close
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });
    
    document.body.appendChild(lightbox);
}

// Open lightbox
function openLightbox(imageSrc) {
    const lightbox = document.getElementById('image-lightbox');
    const lightboxImg = document.getElementById('lightbox-image');
    
    if (!lightbox || !lightboxImg) return;
    
    lightboxImg.src = imageSrc;
    lightbox.classList.add('active');
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
    
    // Update counter
    updateImageCounter();
}

// Close lightbox
function closeLightbox() {
    const lightbox = document.getElementById('image-lightbox');
    if (!lightbox) return;
    
    lightbox.classList.remove('active');
    
    // Restore body scroll
    document.body.style.overflow = '';
}

// Change image in lightbox
function changeImage(direction) {
    if (productImages.length === 0) return;
    
    currentImageIndex += direction;
    
    // Wrap around
    if (currentImageIndex < 0) {
        currentImageIndex = productImages.length - 1;
    }
    if (currentImageIndex >= productImages.length) {
        currentImageIndex = 0;
    }
    
    // Update image
    const lightboxImg = document.getElementById('lightbox-image');
    if (lightboxImg) {
        lightboxImg.src = productImages[currentImageIndex];
    }
    
    // Update counter
    updateImageCounter();
}

// Update image counter
function updateImageCounter() {
    const currentNum = document.getElementById('current-image-num');
    const totalNum = document.getElementById('total-images');
    
    if (currentNum) currentNum.textContent = currentImageIndex + 1;
    if (totalNum) totalNum.textContent = productImages.length;
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    const lightbox = document.getElementById('image-lightbox');
    if (!lightbox || !lightbox.classList.contains('active')) return;
    
    if (e.key === 'Escape') {
        closeLightbox();
    }
    if (e.key === 'ArrowLeft') {
        changeImage(-1);
    }
    if (e.key === 'ArrowRight') {
        changeImage(1);
    }
});

// Touch/Swipe support for mobile
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', function(e) {
    const lightbox = document.getElementById('image-lightbox');
    if (!lightbox || !lightbox.classList.contains('active')) return;
    
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', function(e) {
    const lightbox = document.getElementById('image-lightbox');
    if (!lightbox || !lightbox.classList.contains('active')) return;
    
    touchEndX = e.changedTouches[0].screenX;
    handleLightboxSwipe();
});

function handleLightboxSwipe() {
    if (touchEndX < touchStartX - 50) {
        // Swipe left - next image
        changeImage(1);
    }
    if (touchEndX > touchStartX + 50) {
        // Swipe right - previous image
        changeImage(-1);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLightbox);
} else {
    initLightbox();
}

// Export functions for global access
window.openLightbox = openLightbox;
window.closeLightbox = closeLightbox;
window.changeImage = changeImage;
