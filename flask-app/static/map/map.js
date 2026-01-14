const map = L.map('map').setView([40.0, -105.0], 8);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

fetch("/map/data")
  .then(r => r.json())
  .then(geojson => {
      L.geoJSON(geojson).addTo(map);
  });

