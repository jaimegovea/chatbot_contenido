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


dropzone.addEventListener("dragover", (event) => {
    event.preventDefault();
})

dropzone.addEventListener("drop", (event) => {
    event.preventDefault();
    if (event.dataTransfer.items) {
        files = event.dataTransfer.files;
        var filesToUpload = "";
        for (var counter = 0; counter < files.length; counter++) {
            const file = files[counter];
            const extension = file["type"].split("/")[1];
            console.log(extension)
            if (extension == "pdf") {
                filesToUpload += `<h4><i class="bi bi-filetype-${extension}"></i></h4>`;
            }
            if (extension.includes("vnd.openxmlformats-officedocument.wordprocessingml.document") || extension.includes("msword")) {
                filesToUpload += `<h4><i class="bi bi-filetype-docx"></i></h4>`;
            }
        }
        dropzone.innerHTML = filesToUpload;
    }
})


submitBtn.addEventListener("click", async (event) => {
    event.preventDefault();
    submitBtn.disabled = true;
    spinnerLoader.classList.remove("visually-hidden");
    var totalPDFS = 0;
    var essaysGraded = 0;
    for (var counter = 0; counter < files.length; counter++) {
        const file = files[counter];
        const extension = file["type"].split("/")[1];
        if (extension == "pdf") {
            totalPDFS++;
        }
        if (extension.includes("vnd.openxmlformats-officedocument.wordprocessingml.document") || extension.includes("msword")) {
            totalPDFS++;
        }
    }
    essaysDone.innerHTML = `0/${totalPDFS}`;
    var wasSuccesful = true;
    for (var counter = 0; counter < files.length; counter++) {
        const file = files[counter];
        const extension = file["type"].split("/")[1];
        if (extension == "pdf" || extension.includes("vnd.openxmlformats-officedocument.wordprocessingml.document") || extension.includes("msword")) {
            var data = new FormData();
            data.append("essay", file);
            data.append("criteria", criteria.value);
            data.append("description", description.value);
            await fetch("/assignments", {
                method: "POST",
                headers: { 'X-CSRFToken': csrftoken },
                body: data
            }).then(response => response.json())
                .then(data => {
                    wasSuccesful = data["success"]
                    if (data["success"]) {
                        essaysGraded++;
                    } else {
                        spinnerLoader.classList.add("visually-hidden");
                        myModal.show();
                    }
                }
                )
            essaysDone.innerHTML = `${essaysGraded}/${totalPDFS}`;
        }
    }
    if (wasSuccesful) {
        location.reload();
    }
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