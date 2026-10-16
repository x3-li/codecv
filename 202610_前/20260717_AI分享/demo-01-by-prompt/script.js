(function () {
  const slides = Array.from(document.querySelectorAll(".slide"));
  const prevButton = document.getElementById("prev");
  const nextButton = document.getElementById("next");
  const fullscreenButton = document.getElementById("fullscreen");
  const printPdfButton = document.getElementById("print-pdf");
  const currentPage = document.getElementById("current-page");
  const totalPages = document.getElementById("total-pages");
  const progressBar = document.getElementById("progress-bar");
  let index = 0;

  function render() {
    slides.forEach((slide, slideIndex) => {
      slide.classList.toggle("active", slideIndex === index);
      slide.setAttribute("aria-hidden", slideIndex === index ? "false" : "true");
    });

    currentPage.textContent = String(index + 1);
    totalPages.textContent = String(slides.length);
    progressBar.style.width = `${((index + 1) / slides.length) * 100}%`;
    prevButton.disabled = index === 0;
    nextButton.disabled = index === slides.length - 1;
  }

  function goTo(nextIndex) {
    index = Math.max(0, Math.min(slides.length - 1, nextIndex));
    render();
  }

  async function toggleFullscreen() {
    const root = document.documentElement;
    if (!document.fullscreenElement) {
      if (root.requestFullscreen) {
        await root.requestFullscreen();
      } else if (root.webkitRequestFullscreen) {
        root.webkitRequestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        await document.exitFullscreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      }
    }
  }

  prevButton.addEventListener("click", () => goTo(index - 1));
  nextButton.addEventListener("click", () => goTo(index + 1));
  fullscreenButton.addEventListener("click", () => {
    toggleFullscreen().catch(() => {});
  });
  printPdfButton.addEventListener("click", () => {
    window.print();
  });

  document.addEventListener("keydown", (event) => {
    const key = event.key;
    if (["ArrowRight", "PageDown", " "].includes(key)) {
      event.preventDefault();
      goTo(index + 1);
    }
    if (["ArrowLeft", "PageUp", "Backspace"].includes(key)) {
      event.preventDefault();
      goTo(index - 1);
    }
    if (key.toLowerCase() === "f") {
      toggleFullscreen().catch(() => {});
    }
    if (key.toLowerCase() === "p" && (event.ctrlKey || event.metaKey)) {
      return;
    }
    if (key === "Home") {
      goTo(0);
    }
    if (key === "End") {
      goTo(slides.length - 1);
    }
  });

  let touchStartX = 0;
  document.addEventListener("touchstart", (event) => {
    touchStartX = event.changedTouches[0].clientX;
  }, { passive: true });

  document.addEventListener("touchend", (event) => {
    const delta = event.changedTouches[0].clientX - touchStartX;
    if (Math.abs(delta) > 60) {
      goTo(index + (delta < 0 ? 1 : -1));
    }
  }, { passive: true });

  render();
})();
