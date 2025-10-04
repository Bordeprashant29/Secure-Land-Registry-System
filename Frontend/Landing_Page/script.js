// =======================
// Mobile Menu Toggle
// =======================
const menuToggle = document.querySelector(".menu-toggle");
const navLinks = document.querySelector(".nav-links");

if (menuToggle && navLinks) {
  menuToggle.addEventListener("click", () => {
    navLinks.classList.toggle("active");
  });
}

// =======================
// Contact Form Validation
// =======================
const form = document.getElementById("contactForm");
const formMsg = document.getElementById("formMsg");

if (form) {
  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const message = document.getElementById("message").value.trim();

    if (name === "" || email === "" || message === "") {
      formMsg.style.color = "red";
      formMsg.textContent = "⚠ Please fill in all fields.";
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      formMsg.style.color = "red";
      formMsg.textContent = "⚠ Please enter a valid email.";
      return;
    }

    formMsg.style.color = "green";
    formMsg.textContent = "✅ Message sent successfully!";
    form.reset();
  });
}

// =======================
// Smooth Page Transitions
// =======================
document.addEventListener("DOMContentLoaded", () => {
  document.body.classList.add("fade-in");
});

const links = document.querySelectorAll("a[href]");

links.forEach((link) => {
  if (link.hostname === window.location.hostname) {
    link.addEventListener("click", function (e) {
      const target = this.getAttribute("href");

      // Only animate internal links (skip external + # anchors)
      if (target && !target.startsWith("http") && !target.startsWith("#")) {
        e.preventDefault();
        document.body.classList.remove("fade-in"); // start fade-out

        setTimeout(() => {
          window.location.href = target;
        }, 500); // match with CSS transition time
      }
    });
  }
});

// =======================
// About Page Slider (Fixed & Enhanced)
// =======================
const aboutSlider = document.querySelector(".about-slider");
if (aboutSlider) {
  const slidesContainer = aboutSlider.querySelector(".slides");
  const slides = aboutSlider.querySelectorAll(".slide");
  const prevBtn = aboutSlider.querySelector(".prev");
  const nextBtn = aboutSlider.querySelector(".next");
  const dots = aboutSlider.querySelectorAll(".dot");

  let currentIndex = 0;
  let autoSlide;

  function showSlide(index) {
    if (index < 0) index = slides.length - 1;
    if (index >= slides.length) index = 0;

    slidesContainer.style.transform = `translateX(-${index * 100}%)`;

    slides.forEach((slide, i) => {
      slide.classList.toggle("active", i === index);
    });

    dots.forEach((dot, i) => {
      dot.classList.toggle("active", i === index);
    });

    currentIndex = index;
  }

  function nextSlide() {
    showSlide(currentIndex + 1);
  }

  function prevSlide() {
    showSlide(currentIndex - 1);
  }

  function startAutoSlide() {
    autoSlide = setInterval(nextSlide, 6000);
  }

  function stopAutoSlide() {
    clearInterval(autoSlide);
  }

  nextBtn.addEventListener("click", () => {
    nextSlide();
    stopAutoSlide();
    startAutoSlide();
  });

  prevBtn.addEventListener("click", () => {
    prevSlide();
    stopAutoSlide();
    startAutoSlide();
  });

  dots.forEach((dot, index) => {
    dot.addEventListener("click", () => {
      showSlide(index);
      stopAutoSlide();
      startAutoSlide();
    });
  });

  // Touch swipe for mobile
  let touchStartX = 0;
  let touchEndX = 0;

  aboutSlider.addEventListener("touchstart", (e) => {
    touchStartX = e.changedTouches[0].screenX;
  });

  aboutSlider.addEventListener("touchend", (e) => {
    touchEndX = e.changedTouches[0].screenX;
    if (touchEndX < touchStartX - 50) nextSlide();
    if (touchEndX > touchStartX + 50) prevSlide();
  });

  // Init
  showSlide(0);
  startAutoSlide();
}
