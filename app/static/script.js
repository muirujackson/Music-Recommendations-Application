$(document).ready(function() {
    $('#searchQuery').on('input', function() {
        $('#submitButton').prop('disabled', $(this).val().trim() === '');
    });

    const authButton = $('.authButton');
    const loginStatus = $('.authButton').text();
    const dashboard = $('.dashboard');

       // Click event for the button
    authButton.click(function() {
        if (loginStatus.includes('Logout')) {
            window.location.href = "/logout";
        } else {
            window.location.href = "/login"; // Redirect to the login route
        }
    });

    dashboard.click(function(){
        window.location.href ="/dashboard";
    });

    $('.like-btn').click(function() {
            var trackId = $(this).data('track-id');

            $.ajax({
                type: 'POST',
                url: '/like-song',
                data: { track_id: trackId },
                success: function(response) {
                    // Handle success (optional)
                    $('#successModal').modal('show');
                    console.log(response);
                },
                error: function(error) {
                    // Handle error (optional)
                    console.log(error);
                }
            });
        });
});
