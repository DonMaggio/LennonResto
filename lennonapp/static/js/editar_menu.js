document.getElementById("add-item-form").addEventListener("submit", function(event) {
    event.preventDefault();

    const formData = {
        title: document.getElementById("title").value,
        price: document.getElementById("price").value || null,
        image: document.getElementById("image").value || null,
        description: document.getElementById("description").value,
        category: {
            title: document.getElementById("category_title").value
        }
    };

    fetch('menu', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});