var spinnerLoader = document.getElementById("spinnerLoader");
var submitBtn = document.getElementById("submitBtn");


submitBtn.addEventListener("click", async (event) => {
    spinnerLoader.classList.remove("visually-hidden");
})
