var dropzone = document.getElementById("dropzone");
var btn = document.getElementById("btn");
var files = [];

dropzone.addEventListener("dragover", (event) => {
    event.preventDefault();
})

dropzone.addEventListener("drop", (event) => {
    event.preventDefault();
    if (event.dataTransfer.items) {
        files = event.dataTransfer.items;
        var filesToUpload = "";
        for(var counter = 0; counter < files.length; counter++){
            const file = files[counter].getAsFile();
            const extension = file["type"].split("/")[1];
            if (extension == "pdf"){
                if (files.length > 5 && files.length < 13){
                    filesToUpload += `<h1><i class="bi bi-filetype-${extension}"></i></h1>`;
                }else if(files.length > 13 && files.length < 17){
                    filesToUpload += `<h2><i class="bi bi-filetype-${extension}"></i></h2>`;
                } else if(files.length > 17){
                    filesToUpload += `<h4><i class="bi bi-filetype-${extension}"></i></h4>`;
                }
                 else {
                    filesToUpload += `<h1><i class="bi bi-filetype-${extension}"></i></h1><p>${file["name"]}</p>`;
                }
            }   
        }
        dropzone.innerHTML = filesToUpload;
    }
})

btn.addEventListener("click", async () => {
    for (var counter = 0; counter < files.length; counter++) {
        if (files[counter].kind == "file") {
            const file = files[counter].getAsFile();
            const extension = file["type"].split("/")[1];
            if (extension == "pdf"){
                var data = new FormData();
                data.append("essay", file);
                await fetch("/dropzone", {
                    method: "POST",
                    body: data
                }).then(response => response.json())
                    .then(data => {
                        console.log(data)
                    })
            }
        }
    }
})