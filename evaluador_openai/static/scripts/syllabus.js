var spinnerLoader = document.getElementById("spinnerLoader");
var submitBtn = document.getElementById("submitBtn");
var subject = document.getElementById("subject");
var sessions = document.getElementById("sessions");
var apiKeyIcon = document.getElementById("apiKeyIcon");
var apiKey = document.getElementById("api_key");
var myModal = new bootstrap.Modal('#myModal');
var saveBtn = document.getElementById("saveBtn");
var syllabusRow = document.getElementById("syllabusRow");
var syllabus = [];


submitBtn.addEventListener("click", () => {
    spinnerLoader.classList.remove("visually-hidden");
})

saveBtn.addEventListener("click", async () => {
    var data = new FormData();
    data.append("api_key", apiKey.value);
    await fetch("/update_api_key", {
        method: "POST",
        body: data,
    }).then(response => {
        if (response.ok) {
            location.reload();
        }
    }
    )
})


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