const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('value');

// Obtener el precio del item desde el botón
const price = parseFloat(document.querySelector('.modal-btn').getAttribute('data-item-price'));



document.querySelectorAll('.open-modal-btn').forEach((button, index) => {
    button.addEventListener('click', () => {
        const modal = document.querySelectorAll('.overlay')[index]; // Asegúrate de que estás seleccionando el modal correcto
        modal.style.visibility = 'visible';
        document.body.classList.add('no-scroll');

        const input = modal.querySelector('#miInput');
        const btnIncrease = modal.querySelector('#btn-increase');
        const btnDecrease = modal.querySelector('#btn-decrease');

        btnIncrease.addEventListener('click', function(event) {
            event.preventDefault(); // Evita el comportamiento predeterminado
            input.value = parseInt(input.value) + 1; // Aumenta el número
            updateTotal(modal, input); // Actualiza el total
        });

        btnDecrease.addEventListener('click', function(event) {
            event.preventDefault(); // Evita el comportamiento predeterminado
            input.value = Math.max(1, parseInt(input.value) - 1); // Disminuye el número
            updateTotal(modal, input); // Actualiza el total
        });

        updateTotal(modal, input); // Establece el precio inicial
    });
});


function updateTotal(modal, input) {
    const price = parseFloat(modal.querySelector('.modal-btn').getAttribute('data-item-price'));
    const cantidad = parseInt(input.value, 10);
    const total = price * cantidad; // Calcular el total
    modal.querySelector('.total-price').textContent = '$' + total.toFixed(0); // Actualizar el total
}

document.querySelectorAll('.close-btn').forEach((button, index) => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.overlay')[index].style.visibility = 'hidden';
        document.body.classList.remove('no-scroll'); // Restaurar el scroll
    });
});

// Enviar la cantidad al carrito
document.querySelectorAll('.modal-btn').forEach(button => {
    button.addEventListener('click', function() {
        const itemId = this.getAttribute('data-item-id');
        const modal = this.closest('.modal');
        const overlay = modal.closest('.overlay'); // Obtén el overlay
        const quantity = modal.querySelector('.quantity-input').value; // Obtener el valor de la cantidad
        const errorMessage = modal.querySelector('.error-message'); // Selecciona el mensaje de error

        // Limpiar el mensaje de error antes de realizar la solicitud
        errorMessage.textContent = "";
        errorMessage.style.display = 'none';
        
        const data = {
            menuitem: itemId,
            quantity: parseInt(quantity, 10) // Convertir a número entero
        };

        fetch('/cart/menu-items', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la solicitud');
            }
            
        })
        .then(data => {
            console.log('Éxito:', data);
            // Aquí puedes agregar lógica para mostrar un mensaje de éxito
            window.location.href = '/menu'; // Redirigir a la página de menú
        })
        .catch(error => {
            console.error('Error:', error);
            // Aquí puedes manejar errores
            errorMessage.textContent = "No se pudo agregar el ítem, probablemente ya tengas este plato en tu carrito!"; // Muestra el mensaje de error
            errorMessage.style.display = 'block'; // Muestra el contenedor
        });
    });
});

// Manejar el cambio en el campo de cantidad
document.querySelectorAll('.quantity-input').forEach(input => {
    input.addEventListener('input', function() {
        const price = parseFloat(this.closest('.modal').querySelector('.modal-btn').getAttribute('data-item-price'));
        const cantidad = parseInt(this.value, 10);
        const total = price * cantidad; // Calcular el total
        this.closest('.modal').querySelector('.total-price').textContent = '$' + total.toFixed(2); // Actualizar el total
    });
});



function redirectToItem(itemId) {
    console.log("Redirecting to item:", itemId); 
    window.location.href = '/menu-items/'+itemId ; // Asumiendo que la URL espera un ID
}

