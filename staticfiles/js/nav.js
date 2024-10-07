document.addEventListener('DOMContentLoaded', function() {
    const saludo = document.getElementById('saludo');
    const dropdown = saludo.querySelector('.dropdown');

    saludo.addEventListener('click', function() {
        dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
    });

    // Cerrar el dropdown si se hace clic fuera de él
    document.addEventListener('click', function(event) {
        if (!saludo.contains(event.target)) {
            dropdown.style.display = 'none';
        }
    });
});