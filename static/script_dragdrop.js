// Add dragover event listener to the document
document.addEventListener("dragover", function(event) {
    event.preventDefault();
    var uploadSection = document.getElementById("upload-section");
    uploadSection.classList.add("drag-over");
});

// Add dragleave event listener to the document
document.addEventListener("dragleave", function(event) {
    event.preventDefault();
    console.log("Mouse left upload section"); // Debug message
    var uploadSection = document.getElementById("upload-section");
    uploadSection.classList.remove("drag-over");
});

// Add drop event listener to the document
document.addEventListener("drop", function(event) {
    event.preventDefault();
    var files = event.dataTransfer.files;
    var form = document.getElementById("uploadForm");
    form.querySelector('input[type="file"]').files = files;
    displayFileName();
    var uploadSection = document.getElementById("upload-section");
    uploadSection.classList.remove("drag-over");
});