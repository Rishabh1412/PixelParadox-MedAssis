
function togglesidebar() {
  const navContent = document.querySelector(".my-sidebar");
  const navIcon = document.querySelector(".menu-button");

  if (navContent.style.display === "block") {
    navContent.style.display = "none";
    navContent.style.position="";
    navIcon.classList.remove("fa-times");
    navIcon.classList.add("fa-bars");
  } else {
    navContent.style.display = "block";
    navIcon.classList.remove("fa-bars");
    navIcon.classList.add("fa-times");
    navContent.style.position = "fixed";
    navContent.style.zindex="2";

  }
}