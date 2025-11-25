
(function(){
  const map = L.map('map').setView([20.0, 73.0], 6);

  // OSM tiles
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 20,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  fetch('/api/processed')
    .then(resp => {
      if (!resp.ok) throw new Error('No processed data available');
      return resp.json();
    })
    .then(geojson => {
      let rawLine, cleanedLine;
      const jitterLayer = L.layerGroup().addTo(map);
      const idlingLayer = L.layerGroup().addTo(map);

      // Add raw route
      const rawFeature = geojson.features.find(f => f.properties && f.properties.layer === 'raw_route');
      if (rawFeature) {
        rawLine = L.geoJSON(rawFeature, {
          style: { color: '#1e90ff', weight: 4 }
        }).addTo(map);
      }

      // Add cleaned route
      const cleanedFeature = geojson.features.find(f => f.properties && f.properties.layer === 'cleaned_route');
      if (cleanedFeature) {
        cleanedLine = L.geoJSON(cleanedFeature, {
          style: { color: '#2ecc71', weight: 4 }
        }).addTo(map);
      }

      // Jitter points
      geojson.features.filter(f => f.properties && f.properties.type === 'jitter').forEach(f => {
        const c = f.geometry.coordinates;
        const marker = L.circleMarker([c[1], c[0]], {
          radius: 6, color: '#e74c3c', fillColor: '#e74c3c', fillOpacity: 0.9
        }).bindPopup(`<b>Jitter</b><br>ID: ${f.properties.id}<br>Time: ${f.properties.gpstime}`);
        jitterLayer.addLayer(marker);
      });

      // Idling points
      geojson.features.filter(f => f.properties && f.properties.type === 'idling').forEach(f => {
        const c = f.geometry.coordinates;
        const duration = f.properties.duration_sec.toFixed(0);
        const marker = L.circleMarker([c[1], c[0]], {
          radius: 7, color: '#f1c40f', fillColor: '#f1c40f', fillOpacity: 0.8
        }).bindPopup(`<b>Idling</b><br>${duration} sec<br>${f.properties.start_time} → ${f.properties.end_time}`);
        idlingLayer.addLayer(marker);
      });

      // Fit map to combined bounds
      const group = L.featureGroup([]);
      if (rawLine) group.addLayer(rawLine);
      if (cleanedLine) group.addLayer(cleanedLine);
      group.addLayer(jitterLayer);
      group.addLayer(idlingLayer);
      try {
        map.fitBounds(group.getBounds(), { padding: [20, 20] });
      } catch (_) {
        // fallback view if bounds fail
        map.setView([20.0, 73.0], 6);
      }
    })
    .catch(err => {
      console.error(err);
      alert('Failed to load processed data. Go back and upload a JSON file.');
    });
})();
