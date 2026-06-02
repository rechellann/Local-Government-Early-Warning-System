// ====================================
// LGU DISASTER DASHBOARD JS
// ====================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("Dashboard Loaded Successfully");

    // ==========================
    // CHART.JS
    // ==========================

    const chartCanvas = document.getElementById("incidentChart");

    if (chartCanvas) {

        new Chart(chartCanvas, {
            type: "line",

            data: {
                labels: [
                    "Mon",
                    "Tue",
                    "Wed",
                    "Thu",
                    "Fri",
                    "Sat",
                    "Sun"
                ],

                datasets: [{
                    label: "Incidents",

                    data: [
                        12,
                        19,
                        8,
                        15,
                        24,
                        17,
                        30
                    ],

                    tension: 0.4,

                    fill: true
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });

    }

    // ==========================
    // LEAFLET MAP
    // ==========================

    const mapDiv = document.getElementById("hazardMap");

    if (mapDiv) {

        const map = L.map("hazardMap")
            .setView([11.2433, 125.0040], 12);

        L.tileLayer(
            "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                maxZoom: 19
            }
        ).addTo(map);

        L.marker([11.2433, 125.0040])
            .addTo(map)
            .bindPopup("Tacloban Monitoring Station");

        L.marker([11.22, 125.01])
            .addTo(map)
            .bindPopup("Flood Sensor");

        L.marker([11.26, 124.98])
            .addTo(map)
            .bindPopup("Rainfall Sensor");
    }

    // ==========================
    // FILTER BUTTON
    // ==========================

    const filterBtn =
        document.getElementById("applyFilter");

    if (filterBtn) {

        filterBtn.addEventListener("click", function () {

            const start =
                document.getElementById("startDate").value;

            const end =
                document.getElementById("endDate").value;

            const status =
                document.getElementById("statusFilter").value;

            console.log({
                start,
                end,
                status
            });

            alert(
                "Filters Applied\n\n" +
                "Start: " + start + "\n" +
                "End: " + end + "\n" +
                "Status: " + status
            );

        });

    }

});