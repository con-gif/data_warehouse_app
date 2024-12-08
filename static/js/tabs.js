document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tab-buttons button');

    // Tab switching logic
    buttons.forEach((btn, index) => {
        btn.addEventListener('click', () => {
            buttons.forEach(button => button.classList.remove('active'));
            tabs.forEach(tab => tab.classList.remove('active'));

            btn.classList.add('active');
            tabs[index].classList.add('active');
        });
    });
});