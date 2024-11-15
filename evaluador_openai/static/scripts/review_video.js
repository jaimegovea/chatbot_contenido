var spinnerLoader = document.getElementById("spinnerLoader");
var submitBtn = document.getElementById("submitBtn");


submitBtn.addEventListener("click", () => {
    spinnerLoader.classList.remove("visually-hidden");
})
