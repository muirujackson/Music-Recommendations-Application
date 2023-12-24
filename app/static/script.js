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


    $('#getRecommendation').click(function() {
        $.ajax({
            type: 'GET',
            url: '/recommendation', // Endpoint to fetch recommendations
            success: function(response) {
                // Log the response to check its content and structure
                console.log(response);

                 // Assuming the 'data' returned is JSON containing recommended playlists
                const recommendedPlaylists = $('#recommendedPlaylists');
                recommendedPlaylists.empty(); // Clear previous content


                // Assuming the response is an array of track objects
                response.recommended_songs.forEach(function(track) {

                    if (track.preview_url) {
                        // Create HTML elements for each track (modify as per data structure)
                        var trackElement = `
                            <div id="songs_recommended">
                                <p>Track name: ${track.name}</p>
                                <button class="external-link" data-url="${track.preview_url}">Open External Link</button>
                                <button class="like-btn" data-track-id="${track.id}">Add to Liked Playlists</button>
                                <!-- Modal -->
                                <div class="modal fade" id="successModal-${track.id}" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
                                    <div class="modal-dialog">
                                        <div class="modal-content">
                                            <div class="modal-header">
                                                <h5 class="modal-title" id="exampleModalLabel">Song Added Successfully</h5>
                                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                            </div>
                                            <div class="modal-body">
                                                The song has been added to your playlist.
                                            </div>
                                            <div class="modal-footer">
                                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>`;

                        // Append trackElement to #recommendedPlaylists
                        $('#recommendedPlaylists').append(trackElement);
                    }
                });

                // Add click event for external link buttons
                $('.external-link').click(function() {
                        const externalUrl = $(this).data('url');
                        window.open(externalUrl, '_blank');
                });

                    // Add click event for like buttons
                $('.like-btn').click(function() {
                    const trackId = $(this).data('track-id');
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
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    // $('#getRecommendation').click(function() {
    //     $.get('/recommendation', function(data) {
    //         // Assuming the 'data' returned is JSON containing recommended playlists
    //         const recommendedPlaylists = $('#recommendedPlaylists');
    //         recommendedPlaylists.empty(); // Clear previous content
    //
    //         // Iterate through the recommended playlists and display them
    //         data.forEach(function(playlist) {
    //             // Assuming playlist name is available as 'name' property
    //             recommendedPlaylists.append('<p>' + playlist.name + '</p>');
    //             // Add more details as needed
    //         });
    //     });
    // });

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


    function openModal(message) {
        $('#modalMessage').text(message); // Update the modal message content
        $('#customModal').modal('show'); // Show the modal
    }
    $('.delete-btn').click(function() {
        var trackId = $ (this).data ('track-id');
        var listItem = $(this).closest('.song');

        // Make a DELETE request to Flask route for deleting the track
        $.ajax ({
            url: '/delete-track',
            type: 'DELETE',
            data: JSON.stringify({ track_id: trackId }), // Send data as JSON
            contentType: 'application/json', // Specify content type
            success: function ( response ) {
                // On successful deletion, remove the track from the UI
                listItem.remove();
                openModal (response.message);
                console.log ('Track deleted:', response);
            },
            error: function ( error ) {
                console.error ('Error deleting track:', error);
            }
        });
    });

});
