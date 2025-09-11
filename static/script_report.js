function openTab(evt, tabName) {
    var i, tabContent, tabLinks;
    tabContent = document.getElementsByClassName('tab-content');
    for (i = 0; i < tabContent.length; i++) {
        tabContent[i].style.display = 'none';
    }
    tabLinks = document.getElementsByClassName('subtab');
    for (i = 0; i < tabLinks.length; i++) {
        tabLinks[i].classList.remove('active');
    }
    document.getElementById(tabName).style.display = 'block';
    evt.currentTarget.classList.add('active');
    window.dispatchEvent(new Event('resize'));
    var content = document.querySelector(".collapsible-content");
    if (content) {
        content.style.width = "0";
        content.style.display = "none"; // Hide the content
        content.classList.remove("show");
        content.classList.add("hidden");
    }
}

function openSubTabs(subTabId) {
    // Get all primary tabs and submenus
    let primaryTabs = document.getElementsByClassName("tab");
    let subtabs = document.getElementsByClassName("subtabs");

    // Iterate through all submenus
    for (let i = 0; i < subtabs.length; i++) {
        // If the current submenu is the one associated with the clicked primary tab
        if (subtabs[i].id === subTabId) {
            // Check if the submenu is currently displayed
            if (subtabs[i].style.display === "flex") {
                // If displayed, hide it and deactivate the primary tab
                subtabs[i].style.display = "none";
                primaryTabs[i].classList.remove('active');
            } else {
                // If not displayed, show it and activate the primary tab
                subtabs[i].style.display = "flex";
                primaryTabs[i].classList.add('active');
            }
        } else {
            // Hide other submenus and deactivate their associated primary tabs
            subtabs[i].style.display = "none";
            primaryTabs[i].classList.remove('active');
        }
    }
}




// Hide the loading overlay when the page is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    const loadingOverlay = document.querySelector('.loading-overlay');
    loadingOverlay.style.display = 'none';
});

document.addEventListener("DOMContentLoaded", function () {
    var btn = document.querySelector(".collapsible-button");
    var content = document.querySelector(".collapsible-content");

    btn.addEventListener("click", function () {
        if (content.style.display === "none" || content.style.width === "0px") {
            content.style.width = "450px";
            content.style.display = "block"; // Show the content
            content.classList.remove("hidden");
            content.classList.add("show");
        } else {
            content.style.width = "0";
            content.style.display = "none"; // Hide the content
            content.classList.remove("show");
            content.classList.add("hidden");
        }
    });
});



document.addEventListener("DOMContentLoaded", function () {
    // Query all elements that have a data-file attribute
    const elements = document.querySelectorAll("[data-file]");

    elements.forEach((element) => {
        // Fetch the filename from the data-file attribute
        const fileName = element.getAttribute("data-file");
        console.log('Filename:', fileName);  // Debugging line

        // Initialize the XMLHttpRequest
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                // Populate the innerText of the element with the response text
                element.innerText = xhr.responseText;
            }
        };

        // Configure and send the request
        xhr.open("GET", `/get_text?file_name=${fileName}`, true);
        xhr.send();
    });
});


