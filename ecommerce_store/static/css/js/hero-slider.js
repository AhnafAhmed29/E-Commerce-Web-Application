/* ========================================
   HERO SLIDER JAVASCRIPT
   ======================================== */

/* Hero Slider - Fixed Version */

let currentSlideIndex = 0;
let slideInterval;
const slideChangeTime = 5000; // 5 seconds

// Initialize slider when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeSlider();
});

function initializeSlider() {
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');
    
    if (slides.length === 0) return; // Exit if no slides
    
    // Show first slide
    showSlide(0);
    
    // Start auto-play
    startAutoPlay();
    
    // Pause on hover
    const sliderContainer = document.querySelector('.slider-container');
    if (sliderContainer) {
        sliderContainer.addEventListener('mouseenter', stopAutoPlay);
        sliderContainer.addEventListener('mouseleave', startAutoPlay);
    }
}

function showSlide(index) {
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');
    
    if (slides.length === 0) return;
    
    // Wrap around
    if (index >= slides.length) {
        currentSlideIndex = 0;
    } else if (index < 0) {
        currentSlideIndex = slides.length - 1;
    } else {
        currentSlideIndex = index;
    }
    
    // Hide all slides
    slides.forEach((slide, i) => {
        slide.classList.remove('active');
    });
    
    // Remove active from all dots
    dots.forEach((dot, i) => {
        dot.classList.remove('active');
    });
    
    // Show current slide
    slides[currentSlideIndex].classList.add('active');
    
    // Highlight current dot
    if (dots[currentSlideIndex]) {
        dots[currentSlideIndex].classList.add('active');
    }
}

function changeSlide(direction) {
    stopAutoPlay();
    showSlide(currentSlideIndex + direction);
    startAutoPlay();
}

function currentSlide(index) {
    stopAutoPlay();
    showSlide(index);
    startAutoPlay();
}

function startAutoPlay() {
    stopAutoPlay(); // Clear any existing interval
    slideInterval = setInterval(() => {
        showSlide(currentSlideIndex + 1);
    }, slideChangeTime);
}

function stopAutoPlay() {
    if (slideInterval) {
        clearInterval(slideInterval);
    }
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') {
        changeSlide(-1);
    } else if (e.key === 'ArrowRight') {
        changeSlide(1);
    }
});

// Touch support
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
}, false);

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}, false);

function handleSwipe() {
    if (touchEndX < touchStartX - 50) {
        changeSlide(1);
    }
    if (touchEndX > touchStartX + 50) {
        changeSlide(-1);
    }
}

// Export for inline handlers
window.changeSlide = changeSlide;
window.currentSlide = currentSlide;
