/**
 * main.js
 * -------
 * Client-side logic for LoanAI:
 *  - Bootstrap 5 form validation
 *  - Submit button loading state
 *  - Full-page loading overlay
 *  - Confidence bar animation (result page)
 *  - Reset form helper
 */

'use strict';

/* ==========================================================================
   Predict Form
   ========================================================================== */

/**
 * Initialise prediction form validation and submission handling.
 * Called from predict.html after DOM is ready.
 */
function initPredictForm() {
  const form      = document.getElementById('loanForm');
  const submitBtn = document.getElementById('submitBtn');
  const resetBtn  = document.getElementById('resetBtn');

  if (!form) return;

  // ---- Bootstrap validation on submit ---------------------------------
  form.addEventListener('submit', function (event) {
    if (!form.checkValidity()) {
      event.preventDefault();
      event.stopPropagation();
      form.classList.add('was-validated');
      // Scroll to first error
      const firstInvalid = form.querySelector(':invalid');
      if (firstInvalid) {
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstInvalid.focus();
      }
      return;
    }

    form.classList.add('was-validated');

    // Show loading state on button and overlay
    _setButtonLoading(submitBtn, true);
    _showLoadingOverlay();
  });

  // ---- Extra real-time validation for number inputs -------------------
  const numericIds = ['ApplicantIncome', 'CoapplicantIncome', 'LoanAmount'];
  numericIds.forEach(function (id) {
    const input = document.getElementById(id);
    if (!input) return;
    input.addEventListener('input', function () {
      const val = parseFloat(this.value);
      if (id === 'CoapplicantIncome') {
        this.setCustomValidity(val < 0 ? 'Must be 0 or greater.' : '');
      } else {
        this.setCustomValidity(val > 0 ? '' : 'Must be greater than 0.');
      }
    });
  });

  // ---- Reset button ---------------------------------------------------
  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      form.reset();
      form.classList.remove('was-validated');
      // Reset any custom validity messages
      numericIds.forEach(function (id) {
        const el = document.getElementById(id);
        if (el) el.setCustomValidity('');
      });
    });
  }
}


/* ==========================================================================
   Loading Overlay
   ========================================================================== */

function _showLoadingOverlay() {
  const overlay = document.createElement('div');
  overlay.id = 'loadingOverlay';

  const steps = [
    'Validating your application…',
    'Obtaining IBM IAM token…',
    'Sending data to IBM watsonx.ai…',
    'Running AutoAI model…',
    'Processing prediction result…',
  ];

  overlay.innerHTML = `
    <div class="loading-spinner"></div>
    <div class="loading-steps" id="loadingSteps">
      ${steps.map((s, i) =>
        `<div class="loading-step ${i === 0 ? 'active' : ''}" data-step="${i}">${s}</div>`
      ).join('')}
    </div>
  `;

  document.body.appendChild(overlay);

  // Cycle through steps visually
  let current = 0;
  const stepEls = overlay.querySelectorAll('.loading-step');
  const interval = setInterval(function () {
    if (current < stepEls.length - 1) {
      stepEls[current].classList.remove('active');
      current++;
      stepEls[current].classList.add('active');
    } else {
      clearInterval(interval);
    }
  }, 900);
}


/* ==========================================================================
   Submit button loading state
   ========================================================================== */

function _setButtonLoading(btn, isLoading) {
  if (!btn) return;
  const textSpan    = btn.querySelector('.btn-text');
  const loadingSpan = btn.querySelector('.btn-loading');
  if (!textSpan || !loadingSpan) return;

  if (isLoading) {
    textSpan.classList.add('d-none');
    loadingSpan.classList.remove('d-none');
    btn.disabled = true;
  } else {
    textSpan.classList.remove('d-none');
    loadingSpan.classList.add('d-none');
    btn.disabled = false;
  }
}


/* ==========================================================================
   Result Page — Confidence Bar Animation
   ========================================================================== */

/**
 * Animates the confidence progress bar on the result page.
 * Called from result.html after DOM is ready.
 */
function animateConfidenceBar() {
  const bar = document.querySelector('.confidence-bar[data-target]');
  if (!bar) return;

  const target = parseFloat(bar.getAttribute('data-target')) || 0;

  // Use requestAnimationFrame for smooth animation
  requestAnimationFrame(function () {
    setTimeout(function () {
      bar.style.width = Math.min(target, 100) + '%';
    }, 300);  // slight delay for dramatic effect
  });
}


/* ==========================================================================
   Navbar scroll effect
   ========================================================================== */

(function initNavbarScroll() {
  const navbar = document.querySelector('.navbar-custom');
  if (!navbar) return;

  window.addEventListener('scroll', function () {
    if (window.scrollY > 20) {
      navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,.35)';
    } else {
      navbar.style.boxShadow = 'none';
    }
  }, { passive: true });
}());


/* ==========================================================================
   Scroll-reveal: fade in elements as they enter the viewport
   ========================================================================== */

(function initScrollReveal() {
  const elements = document.querySelectorAll(
    '.feature-card, .step-card, .about-card, .feature-info-card'
  );

  if (!elements.length || !('IntersectionObserver' in window)) return;

  // Set initial hidden state
  elements.forEach(function (el) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.45s ease, transform 0.45s ease';
  });

  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12 }
  );

  elements.forEach(function (el) { observer.observe(el); });
}());
