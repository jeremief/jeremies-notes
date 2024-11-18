// Single initialization when document is ready
$(document).ready(function() {
    console.log('Document ready');
    
    // Apply night mode immediately if needed
    const isNightMode = localStorage.getItem('nightMode') === 'true';
    if (isNightMode) {
        applyNightMode(false);
    }
    
    // Set up click handler for night mode button
    $('.night-day-button').on('click', toggleNightMode);
    
    // Initialize theme
    const isModernTheme = localStorage.getItem('modernTheme') === 'true';
    if (isModernTheme) {
        applyModernTheme();
    }
    
    // Set up theme toggle handler
    $('.theme-toggle-button').on('click', toggleTheme);
});

function applyNightMode(withTransition = false) {
    if (withTransition) {
        // Add transition class only when toggling via button
        $('body, p, h2, .stage, .topic, .menu, .point, .intro-text, .summary, .code, .comment, .text-container, .menu-link, .button-container, .night-day-button, a').addClass('use-transition');
    }
    
    // Apply night mode classes
    $("body").addClass("nightmode-body");
    $("p").addClass("nightmode-p");
    $("h2").addClass("nightmode-h2");
    $(".stage").addClass("nightmode-stage");
    $(".topic").addClass("nightmode-topic");
    $(".menu").addClass("nightmode-menu");
    $(".point").addClass("nightmode-point");
    $(".intro-text").addClass("nightmode-intro-text");
    $(".summary").addClass("nightmode-summary");
    $(".code").addClass("nightmode-code");
    $(".comment").addClass("nightmode-comment");
    $(".text-container").addClass("nightmode-text-container");
    $(".menu-link").addClass("nightmode-menu-link");
    $(".button-container").addClass("nightmode-button-container");
    $(".night-day-button").addClass("nightmode-night-day-button");
    $("a").addClass("nightmode-normal-link");
    
    if (withTransition) {
        // Remove transition class after animation completes
        setTimeout(() => {
            $('body, p, h2, .stage, .topic, .menu, .point, .intro-text, .summary, .code, .comment, .text-container, .menu-link, .button-container, .night-day-button, a').removeClass('use-transition');
        }, 300);
    }
}

function removeNightMode(withTransition = false) {
    if (withTransition) {
        // Add transition class to elements that need it
        $('body, p, h2, .stage, .topic, .menu, .point, .intro-text, .summary, .code, .comment, .text-container, .menu-link, .button-container, .night-day-button, a').addClass('use-transition');
    }
    
    // Remove night mode classes
    $("body").removeClass("nightmode-body");
    $("p").removeClass("nightmode-p");
    $("h2").removeClass("nightmode-h2");
    $(".stage").removeClass("nightmode-stage");
    $(".topic").removeClass("nightmode-topic");
    $(".menu").removeClass("nightmode-menu");
    $(".point").removeClass("nightmode-point");
    $(".intro-text").removeClass("nightmode-intro-text");
    $(".summary").removeClass("nightmode-summary");
    $(".code").removeClass("nightmode-code");
    $(".comment").removeClass("nightmode-comment");
    $(".text-container").removeClass("nightmode-text-container");
    $(".menu-link").removeClass("nightmode-menu-link");
    $(".button-container").removeClass("nightmode-button-container");
    $(".night-day-button").removeClass("nightmode-night-day-button");
    $("a").removeClass("nightmode-normal-link");
    
    if (withTransition) {
        // Remove transition class after animation completes
        setTimeout(() => {
            $('body, p, h2, .stage, .topic, .menu, .point, .intro-text, .summary, .code, .comment, .text-container, .menu-link, .button-container, .night-day-button, a').removeClass('use-transition');
        }, 300);
    }
}

function toggleNightMode() {
    const isCurrentlyNightMode = $("body").hasClass("nightmode-body");
    console.log('Current night mode:', isCurrentlyNightMode);

    if (isCurrentlyNightMode) {
        removeNightMode(true);  // true enables transition
        localStorage.setItem('nightMode', 'false');
    } else {
        applyNightMode(true);   // true enables transition
        localStorage.setItem('nightMode', 'true');
    }
}
function searchWikipedia(event) {
    event.preventDefault();
    
    const searchTerm = document.getElementById('searchInput').value;
    const resultDiv = document.getElementById('searchResult');
    
    if (!searchTerm) {
        resultDiv.innerHTML = 'Please enter a search term';
        resultDiv.classList.add('error');
        return;
    }

    // Show loading state
    resultDiv.innerHTML = 'Loading...';
    resultDiv.classList.remove('error');

    fetch('/api', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({ search: searchTerm })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            resultDiv.innerHTML = `Error: ${data.error}`;
            resultDiv.classList.add('error');
        } else {
            resultDiv.innerHTML = data.summary;
            resultDiv.classList.remove('error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        resultDiv.innerHTML = `Error: ${error.message}`;
        resultDiv.classList.add('error');
    });
}

// Add event listener when the document loads
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('searchForm');
    if (form) {
        form.addEventListener('submit', searchWikipedia);
    }
});

function applyModernTheme() {
    $('body').addClass('modern-theme');
    $('.theme-toggle-button').text('Classic Theme');
}

function removeModernTheme() {
    $('body').removeClass('modern-theme');
    $('.theme-toggle-button').text('Modern Theme');
}

function toggleTheme() {
    const isModernTheme = $('body').hasClass('modern-theme');
    
    if (isModernTheme) {
        removeModernTheme();
        localStorage.setItem('modernTheme', 'false');
    } else {
        applyModernTheme();
        localStorage.setItem('modernTheme', 'true');
    }
}
