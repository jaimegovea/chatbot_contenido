var spinnerLoader = document.getElementById("spinnerLoader");
var essaysDone = document.getElementById("essaysDone");
var submitBtn = document.getElementById("submitBtn");
var essayRow = document.getElementById("essayRow");
var essayInput = document.getElementById("essayInput");
var criteria = document.getElementById("criteria");
var description = document.getElementById("description");
let files = [];
var essays = [];
var apiKeyIcon = document.getElementById("apiKeyIcon");
var apiKey = document.getElementById("api_key");
var myModal = new bootstrap.Modal('#myModal');
var saveBtn = document.getElementById("saveBtn");
var dropzone = document.getElementById("dropzone");

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


submitBtn.addEventListener("click", async (event) => {
    spinnerLoader.classList.remove("visually-hidden");
})

saveBtn.addEventListener("click", async () => {
    var data = new FormData();
    data.append("api_key", apiKey.value);
    await fetch("/update_api_key", {
        method: "POST",
        headers: { 'X-CSRFToken': csrftoken },
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