document.addEventListener("submit", (event) => {
  const button = event.submitter;
  if (button && button.classList.contains("shine")) {
    button.textContent = "Sending payment…";
    button.disabled = true;
  }
});
