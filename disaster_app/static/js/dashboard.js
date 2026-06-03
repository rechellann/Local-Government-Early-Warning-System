document.addEventListener("DOMContentLoaded", function () {

    console.log("LGU Dashboard Loaded");

    // Sidebar active highlight
    const links = document.querySelectorAll(".sidebar a");

    links.forEach(link => {
        link.addEventListener("click", function () {
            links.forEach(l => l.classList.remove("active"));
            this.classList.add("active");
        });
    });

});