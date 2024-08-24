const texts = ["Health companion", "Health assistant", "Healthcare helper","Healthcare guide"];
let currentIndex = 0;

document.addEventListener("DOMContentLoaded", () => {
  const textElement = document.querySelector(".textchange");

  function changeText() {
    textElement.textContent = texts[currentIndex];
    currentIndex = (currentIndex + 1) % texts.length;
  }

  changeText(); // Call immediately to set the initial text
  setInterval(changeText, 3000);
});


