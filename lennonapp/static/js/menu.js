document.querySelectorAll('.open-modal-btn').forEach((button, index) => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.overlay')[index].style.visibility = 'visible';
        document.body.classList.add('no-scroll'); // Bloquear el scroll
    });
});

document.querySelectorAll('.close-btn').forEach((button, index) => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.overlay')[index].style.visibility = 'hidden';
        document.body.classList.remove('no-scroll'); // Restaurar el scroll
    });
});