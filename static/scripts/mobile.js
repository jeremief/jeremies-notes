document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const menuContainer = document.querySelector('.left-menu-container');
    let menuOpen = false;

    // Hide menu toggle on desktop
    function checkScreenSize() {
        if (window.innerWidth > 768) {
            menuToggle.style.display = 'none';
            menuContainer.style.transform = 'none';
            // Reset menu state for desktop
            menuOpen = false;
        } else {
            menuToggle.style.display = 'block';
            if (!menuOpen) {
                menuContainer.style.transform = 'translateY(-100%)';
            }
        }
    }

    // Toggle menu with theme support
    menuToggle.addEventListener('click', function(e) {
        e.stopPropagation(); // Prevent event bubbling
        menuOpen = !menuOpen;
        menuContainer.style.transform = menuOpen ? 'translateY(0)' : 'translateY(-100%)';
        menuToggle.textContent = menuOpen ? '✕' : '☰';
        
        // Add active class for additional styling
        menuContainer.classList.toggle('active', menuOpen);
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        if (menuOpen && 
            !menuContainer.contains(event.target) && 
            !menuToggle.contains(event.target)) {
            menuOpen = false;
            menuContainer.style.transform = 'translateY(-100%)';
            menuToggle.textContent = '☰';
            menuContainer.classList.remove('active');
        }
    });

    // Handle window resize
    window.addEventListener('resize', checkScreenSize);
    checkScreenSize();
}); 