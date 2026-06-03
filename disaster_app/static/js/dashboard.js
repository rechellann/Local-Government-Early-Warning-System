// Sidebar active state handler
document.addEventListener("DOMContentLoaded", function () {

    let links = document.querySelectorAll(".sidebar a");

    links.forEach(link => {
        link.addEventListener("click", function () {

            links.forEach(l => l.classList.remove("active"));
            this.classList.add("active");

        });
    });

});