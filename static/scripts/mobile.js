document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const menuContainer = document.querySelector('.left-menu-container');
    let menuOpen = false;

    // Hide menu toggle on desktop
    function checkScreenSize() {
        if (window.innerWidth > 768) {
            menuToggle.style.display = 'none';
            menuContainer.style.transform = 'none';
        } else {
            menuToggle.style.display = 'block';
            if (!menuOpen) {
                menuContainer.style.transform = 'translateY(-100%)';
            }
        }
    }

    // Toggle menu
    menuToggle.addEventListener('click', function() {
        menuOpen = !menuOpen;
        menuContainer.style.transform = menuOpen ? 'translateY(0)' : 'translateY(-100%)';
        menuToggle.textContent = menuOpen ? '✕' : '☰';
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        if (menuOpen && 
            !menuContainer.contains(event.target) && 
            !menuToggle.contains(event.target)) {
            menuOpen = false;
            menuContainer.style.transform = 'translateY(-100%)';
            menuToggle.textContent = '☰';
        }
    });

    // Handle window resize
    window.addEventListener('resize', checkScreenSize);
    checkScreenSize();
}); 