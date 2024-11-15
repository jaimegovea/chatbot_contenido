var passwordIcon = document.getElementById("passwordIcon");
var password = document.getElementById("password");

passwordIcon.isVisible = false;

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
