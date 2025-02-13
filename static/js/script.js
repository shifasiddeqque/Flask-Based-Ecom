document.addEventListener('DOMContentLoaded', function () {
    let currentSlide = 0;
    const slides = document.querySelectorAll('.carousel-slide');
    const totalSlides = slides.length;
    const dots = document.querySelectorAll('.dot');
    const carousel = document.querySelector('.carousel');
    
    // Update the displayed slide based on the index
    function showSlide(index) {
        if (index >= totalSlides) {
            currentSlide = 0; // Loop back to the first slide
        } else if (index < 0) {
            currentSlide = totalSlides - 1; // Loop back to the last slide
        } else {
            currentSlide = index;
        }

        // Move the carousel
        carousel.style.transform = `translateX(-${currentSlide * 100}%)`;

        // Update dots
        updateDots();
    }

    // Update the dots when a new slide is shown
    function updateDots() {
        dots.forEach((dot, index) => {
            if (index === currentSlide) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    // Move to the next or previous slide
    function moveSlide(step) {
        showSlide(currentSlide + step);
    }

    // Add event listeners to dots for direct navigation
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            showSlide(index);
        });
    });

    // Initialize the carousel
    showSlide(currentSlide);

    // Auto-slide every 3 seconds
    let slideInterval = setInterval(() => {
        moveSlide(1);
    }, 3000);

    // Pause the sliding when hovering over the carousel
    const carouselContainer = document.querySelector('.carousel-container');
    carouselContainer.addEventListener('mouseenter', () => {
        clearInterval(slideInterval);
    });

    // Resume the sliding when mouse leaves the carousel
    carouselContainer.addEventListener('mouseleave', () => {
        slideInterval = setInterval(() => {
            moveSlide(1);
        }, 3000);
    });
});

document.addEventListener('DOMContentLoaded', function () {
    var variantSelect = document.getElementById('variant-select');
    var displayedPrice = document.getElementById('displayed-price');
    
    // Make sure the element exists before adding the event listener
    if (variantSelect && displayedPrice) {
        variantSelect.addEventListener('change', function() {
            var selectedOption = this.options[this.selectedIndex];
            var price = selectedOption.getAttribute('data-price');
            
            // Update the displayed price in your UI
            displayedPrice.innerText = 'Price: ₹' + price;
        });
    }
});