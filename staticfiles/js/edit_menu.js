const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('value');

document.getElementById("edit-item-form").addEventListener("submit", function(event) {
    event.preventDefault();

    const formData = {
        title: document.getElementById("title").value,
        price: document.getElementById("price").value || null,
        image: document.getElementById("image").files[0], // Obtén el archivo de imagen
        existingImage: document.getElementById("existing-image").value, // Imagen existente
        description: document.getElementById("description").value,
        category: document.getElementById("category").value
    };

    // Si no hay archivo de imagen, intenta usar la imagen existente
    if (!formData.image && formData.existingImage) {
        // Cargar la imagen existente como un archivo
        fetch(formData.existingImage)
            .then(response => response.blob())
            .then(blob => {
                const file = new File([blob], "existing_image.jpg", { type: blob.type }); // Cambia el nombre según necesites
                // Agrega los datos al FormData
                const data = new FormData();
                data.append('title', formData.title);
                data.append('price', formData.price);
                data.append('image', file); // Usa el archivo cargado
                data.append('description', formData.description);
                data.append('category', formData.category);

                return fetch('', {
                    method: 'PUT',
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    body: data
                });
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json();
                }
            })
            .then(data => {
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    } else {
        // Si hay un nuevo archivo, simplemente lo envía
        const data = new FormData();
        data.append('title', formData.title);
        data.append('price', formData.price);
        data.append('image', formData.image);
        data.append('description', formData.description);
        data.append('category', formData.category);

        fetch('', {
            method: 'PUT',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: data
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                return response.json();
            }
        })
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
});

