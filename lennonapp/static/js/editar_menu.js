const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('value');

document.getElementById("add-item-form").addEventListener("submit", function(event) {
    event.preventDefault();

    const formData = {
        title: document.getElementById("title").value,
        price: document.getElementById("price").value || null,
        image: document.getElementById("image").files[0] || null,
        description: document.getElementById("description").value,
        category: {
            title: document.getElementById("category_title").value
        }
    };
    // Si estás subiendo una imagen, usa FormData
    const data = new FormData();
    data.append('title', formData.title);
    data.append('price', formData.price);
    data.append('image', formData.image); // Asegúrate de que sea un archivo
    data.append('description', formData.description);
    data.append('category[title]', formData.category.title);

    fetch('', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: data
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.message || 'Error en la solicitud');
            });
        }
        return response;
    })
    .then(data => {
        console.log('Success:', data);
        // Puedes redirigir o mostrar un mensaje de éxito aquí
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});