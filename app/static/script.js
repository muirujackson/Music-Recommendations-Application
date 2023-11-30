$(document).ready(function() {
    $('#searchQuery').on('input', function() {
        $('#submitButton').prop('disabled', $(this).val().trim() === '');
    });

    const authButton = $('.authButton');
    const loginStatus = $('.authButton').text();

       // Click event for the button
    authButton.click(function() {
        if (loginStatus.includes('Logout')) {
            window.location.href = "/logout";
        } else {
            window.location.href = "/login"; // Redirect to the login route
        }
    });
});
