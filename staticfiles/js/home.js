function initMap() {
    const location = { lat: -34.6208, lng: -58.4333 }; // Cambia a la latitud y longitud de tu ubicación
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 15,
        center: location,
    });
    const marker = new google.maps.Marker({
        position: location,
        map: map,
    });
}