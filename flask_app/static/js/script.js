// Este archivo contiene interacciones pequeñas de la página, como confirmaciones y contadores.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });
  document.querySelectorAll("textarea[maxlength]").forEach((textarea) => {
    const update = () => {
      const max = Number(textarea.maxLength);
      let counter = textarea.parentElement.querySelector(".char-counter");
      if (!counter) {
        counter = document.createElement("div");
        counter.className = "form-text char-counter text-end";
        textarea.insertAdjacentElement("afterend", counter);
      }
      counter.textContent = `${textarea.value.length} / ${max} caracteres`;
    };
    textarea.addEventListener("input", update);
    update();
  });
});
