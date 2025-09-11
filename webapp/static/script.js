function showLoadingOverlay() {
    var overlay = document.getElementById('loading-overlay');
    overlay.style.display = 'flex';
    var uploadButton = document.getElementById('uploadButton');
}

function displayFileName() {
    const fileInput = document.getElementById("file");
    const selectedFile = document.getElementById("selected-file");
    const uploadButton = document.getElementById("upload-button");
    const loadingOverlay = document.getElementById("loading-overlay"); // Add this line

    if (fileInput.files.length > 0) {
        selectedFile.textContent = "Selected file: " + fileInput.files[0].name;
        uploadButton.disabled = false;
    } else {
        selectedFile.textContent = "";
        uploadButton.disabled = true;
    }
}
