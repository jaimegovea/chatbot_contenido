var apiKeyIcon = document.getElementById("apiKeyIcon");
var apiKey = document.getElementById("api_key");
var myModal = new bootstrap.Modal('#myModal');
var saveBtn = document.getElementById("saveBtn");

apiKeyIcon.isVisible = false;

apiKeyIcon.addEventListener("click", () => {
    apiKeyIcon.isVisible = !apiKeyIcon.isVisible;
    if (apiKeyIcon.isVisible) {
        apiKeyIcon.innerHTML = '<i class="bi bi-eye"></i>'
        apiKey.type = "text";
    } else {
        apiKeyIcon.innerHTML = '<i class="bi bi-eye-slash"></i>'
        apiKey.type = "password";
    }
});