const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('value');

document.addEventListener("DOMContentLoaded", function() {
    // Selecciona todos los botones "Completado"
    const buttons = document.querySelectorAll('.btn-ver-detalles');

    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const pedidoId = this.getAttribute('data-id');
            const currentStatus = this.getAttribute('data-status') === 'True'; // Suponiendo que tienes un atributo data-status

            // Cambia el estado
            const newStatus = !currentStatus;

            // Realiza la solicitud PATCH
            fetch(`/orders/change/${pedidoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken // Agrega el token CSRF
                },
                body: JSON.stringify({ status: newStatus }) // Cuerpo de la solicitud en formato JSON
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json();
                }
            })
            .then(data => {
                console.log('Pedido actualizado:', data);
                // Actualiza el atributo data-status del botón
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
});
