$(document).ready(function() {
    $('#show-login-modal').click(function() {
        $('#loginModal').modal('show');
    });

    $('#show-signup-modal').click(function() {
        $('#signupModal').modal('show');
    });

    $('#show-signup-form').click(function() {
        $('#loginModal').modal('hide');
        $('#signupModal').modal('show');
    });

    $('#back-to-login').click(function() {
        $('#signupModal').modal('hide');
        $('#loginModal').modal('show');
    });

    $('#login-form').submit(function(event) {
        event.preventDefault();
        var formData = $(this).serialize();
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            success: function(response) {
                window.location.reload(); // Reload page after successful login
            },
            error: function(xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText); // Log error to console
            }
        });
    });

    $('#signup-form').submit(function(event) {
        event.preventDefault();
        var formData = $(this).serialize();
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            success: function(response) {
                $('#signupModal').modal('hide');
                $('#loginModal').modal('show');
            },
            error: function(xhr, errmsg, err) {
                console.log(xhr.status + ": " + xhr.responseText); // Log error to console
            }
        });
    });
});

// Price range update logic
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}

const debouncedUpdatePriceRange = debounce((value) => {
    document.getElementById('price-range-value').innerText = value;
    let url = new URL(window.location.href);
    url.searchParams.set('max_price', value);
    window.location.href = url.toString();
}, 100);

document.getElementById('price-range').addEventListener('input', (event) => {
    const value = event.target.value;
    debouncedUpdatePriceRange(value);
});

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const maxPrice = urlParams.get('max_price');
    if (maxPrice) {
        document.getElementById('price-range').value = maxPrice;
        document.getElementById('price-range-value').innerText = maxPrice;
    }
});