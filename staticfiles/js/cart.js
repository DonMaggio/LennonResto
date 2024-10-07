const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('value');

document.querySelectorAll('.cart__item-edit').forEach(button => {
    button.addEventListener('click', function() {
        const itemId = this.getAttribute('data-item-menuid');

        const data = {
            menuitem: itemId,
        };

        fetch('/cart/menu-items', {
            method: 'DELETE',
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
            return response;
        })
        .then(data => {
            console.log('Éxito:', data);
            // Aquí puedes actualizar la UI, por ejemplo, eliminar el item de la lista
            const cartItem = button.closest('.cart__item');
            //cartItem.remove();// Esto elimina el item del carrito
            location.reload(); 
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});

document.querySelectorAll('.confirm-order').forEach(button => {
    button.addEventListener('click', function() {
        const userId = this.getAttribute('data-user-id');

        const orderdata = {
            user: userId,
        };

        // Mostrar el loader
        const loader = document.getElementById("loader");
        loader.style.display = "flex";

        fetch('/orders/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(orderdata)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la solicitud');
            }
            return response;
        })
        .then(data => {
            console.log('Éxito:', data);
            // Aquí puedes agregar lógica para mostrar un mensaje de éxito
            const modal = document.getElementById("success-modal");
            //Mostrar Modal
            modal.style.display = "block";

            // Cerrar el modal y refrescar la página
            const closeModal = document.querySelector('.close');
            closeModal.onclick = function() {
                modal.style.display = "none";
                loader.style.display = "none"; // Ocultar loader
                location.reload();
            };

            // Cerrar el modal si se hace clic fuera de él
            window.onclick = function(event) {
                if (event.target === modal) {
                    modal.style.display = "none";
                    loader.style.display = "none"; // Ocultar loader
                    location.reload();
                }
            };
        })
        .catch(error => {
            console.error('Error:', error);
            // Aquí puedes manejar errores
        })

        .then(() => {
            // Ocultar el loader al final
            loader.style.display = "none";
        });
    });
});
