var passwordIcon = document.getElementById("passwordIcon");
var password = document.getElementById("password");
var apiKeyIcon = document.getElementById("apiKeyIcon");
var apiKey = document.getElementById("api_key");

passwordIcon.isVisible = false;
apiKeyIcon.isVisible = false;

passwordIcon.addEventListener("click", () => {
    passwordIcon.isVisible = !passwordIcon.isVisible;
    if (passwordIcon.isVisible) {
        passwordIcon.innerHTML = '<i class="bi bi-eye"></i>'
        password.type = "text";
    } else {
        passwordIcon.innerHTML = '<i class="bi bi-eye-slash"></i>'
        password.type = "password";
    }
});

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