(() => {
  // Horizontal screenshot gallery scroll controls
  const track = document.querySelector('[data-gallery-track]');
  const prevScrollBtn = document.querySelector('[data-gallery-prev]');
  const nextScrollBtn = document.querySelector('[data-gallery-next]');

  if (track && prevScrollBtn && nextScrollBtn) {
    const getStep = () => Math.max(track.clientWidth * 0.72, 280);
    prevScrollBtn.addEventListener('click', () => {
      track.scrollBy({ left: -getStep(), behavior: 'smooth' });
    });
    nextScrollBtn.addEventListener('click', () => {
      track.scrollBy({ left: getStep(), behavior: 'smooth' });
    });
  }

  // Accessible native <dialog> screenshot lightbox
  const dialog = document.getElementById('screenshot-lightbox');
  const triggers = Array.from(document.querySelectorAll('[data-lightbox-index]'));

  if (!dialog || triggers.length === 0) return;

  const imgEl = dialog.querySelector('[data-lightbox-img]');
  const captionEl = dialog.querySelector('[data-lightbox-caption]');
  const counterEl = dialog.querySelector('[data-lightbox-counter]');
  const prevBtn = dialog.querySelector('[data-lightbox-prev]');
  const nextBtn = dialog.querySelector('[data-lightbox-next]');
  const closeBtn = dialog.querySelector('[data-lightbox-close]');

  const items = triggers.map((btn) => ({
    src: btn.dataset.src,
    alt: btn.dataset.alt || '',
    caption: btn.dataset.caption || '',
  }));

  let activeIndex = 0;

  const render = (index) => {
    activeIndex = (index + items.length) % items.length;
    const item = items[activeIndex];
    imgEl.src = item.src;
    imgEl.alt = item.alt;
    captionEl.textContent = item.caption;
    counterEl.textContent = `${activeIndex + 1} / ${items.length}`;
  };

  triggers.forEach((btn) => {
    btn.addEventListener('click', () => {
      render(Number(btn.dataset.lightboxIndex) || 0);
      if (typeof dialog.showModal === 'function') {
        dialog.showModal();
      } else {
        dialog.setAttribute('open', '');
      }
    });
  });

  prevBtn?.addEventListener('click', () => render(activeIndex - 1));
  nextBtn?.addEventListener('click', () => render(activeIndex + 1));
  closeBtn?.addEventListener('click', () => dialog.close());

  // Light-dismiss fallback when clicking backdrop outside modal content
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) {
      dialog.close();
    }
  });

  dialog.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') {
      event.preventDefault();
      render(activeIndex - 1);
    } else if (event.key === 'ArrowRight') {
      event.preventDefault();
      render(activeIndex + 1);
    }
  });
})();
