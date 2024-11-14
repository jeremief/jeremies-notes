function nightmode() {

    $("body").toggleClass("nightmode-body");
    $("p").toggleClass("nightmode-p");
    $("h2").toggleClass("nightmode-h2");
    $(".stage").toggleClass("nightmode-stage");
    $(".topic").toggleClass("nightmode-topic");
    $(".menu").toggleClass("nightmode-menu");
    $(".point").toggleClass("nightmode-point");
    $(".intro-text").toggleClass("nightmode-intro-text");
    $(".summary").toggleClass("nightmode-summary");
    $(".code").toggleClass("nightmode-code");
    $(".comment").toggleClass("nightmode-comment");
    $(".text-container").toggleClass("nightmode-text-container");
    $(".menu-link").toggleClass("nightmode-menu-link");
    $(".button-container").toggleClass("nightmode-button-container");
    $(".night-day-button").toggleClass("nightmode-night-day-button");
    $("a").toggleClass("nightmode-normal-link");
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
