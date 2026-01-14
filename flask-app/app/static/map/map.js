// map.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize map centered on the USA
    var map = L.map('map').setView([39.8283, -98.5795], 4);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Optional: add a marker
    L.marker([39.8283, -98.5795]).addTo(map)
        .bindPopup('Center of USA')
        .openPopup();
});


//const map = L.map('map').setView([40.0, -105.0], 8);
//
//L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
//  attribution: '© OpenStreetMap contributors'
//}).addTo(map);
//
//fetch("/map/data")
//  .then(r => r.json())
//  .then(geojson => {
//      L.geoJSON(geojson).addTo(map);
//  });
//
