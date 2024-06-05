document.addEventListener('DOMContentLoaded', function() {
    const voiceSelect = document.getElementById('voiceSelect');
    const artStyleSelect = document.getElementById('artStyleSelect');
    const musicGenreSelect = document.getElementById('musicGenreSelect');
    const generateButton = document.getElementById('generateButton');
    const voiceExamplePlayer = document.getElementById('voiceExamplePlayer');
    const generatedAudioPlayer = document.getElementById('generatedAudioPlayer');
    const outputContainer = document.getElementsByClassName('outputContainer')[0];
    const loadingBar = document.getElementById('loadingBar');
    const outputImage = document.getElementById('outputImage');

    const voiceSamples = {
        "alloy": "/static/static/audio_samples/alloy.mp3",
        "echo": "/static/static/audio_samples/echo.mp3",
        "fable": "/static/static/audio_samples/fable.mp3",
        "onyx": "/static/static/audio_samples/onyx.mp3",
        "nova": "/static/static/audio_samples/nova.mp3",
        "shimmer": "/static/static/audio_samples/shimmer.mp3"
    };

    function playVoiceSample(voice) {
        const audio = new Audio(voiceSamples[voice]);
        audio.play();
    }

    voiceSelect.addEventListener('change', function() {
        const selectedVoice = voiceSelect.value;
        playVoiceSample(selectedVoice);
    });

    generateButton.addEventListener('click', function() {
        const textInput = document.getElementById('textInput').value;
        const selectedVoice = voiceSelect.value;
        const selectedArtStyle = artStyleSelect.value;
        const selectedMusicGenre = musicGenreSelect.value;

        // Clear any previous error message
        const previousError = document.getElementById('error-message');
        if (previousError) {
            previousError.remove();
        }

        outputContainer.style.display = 'flex';
        loadingBar.style.width = '0%';
        loadingBar.innerText = 'Loading...';

        // Reset the output elements
        generatedAudioPlayer.style.display = 'none';
        outputImage.style.display = 'none';
        loadingBar.innerText = 'Loading...';
        loadingBar.style.display = 'block'; // Ensure loading bar is visible
        generatedAudioPlayer.style.display = 'none';
        outputImage.style.display = 'none';
        generatedAudioPlayer.src = '';
        outputImage.src = '';

        // Scroll to the output container
        const offset = outputContainer.getBoundingClientRect().top + window.scrollY - (window.innerHeight / 2) + (loadingBar.offsetHeight / 2);
        window.scrollTo({ top: offset, behavior: 'smooth' });

        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: textInput,
                voice: selectedVoice,
                artStyle: selectedArtStyle,
                musicGenre: selectedMusicGenre
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            if (data.audioUrl && data.imageUrl) {
                loadingBar.style.width = '100%';
                loadingBar.innerText = 'Complete';
                setTimeout(() => {
                    generatedAudioPlayer.src = data.audioUrl;
                    outputImage.src = data.imageUrl;
                    generatedAudioPlayer.style.display = 'block';
                    outputImage.style.display = 'block';
                    loadingBar.style.display = 'none';
                }, 500);
            } else {
                throw new Error('Failed to load resources');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            outputContainer.style.display = 'none';
            loadingBar.style.width = '100%';
            loadingBar.style.backgroundColor = 'red';
            loadingBar.innerText = 'Failed!';

            // Display error message to the user
            const errorMessage = document.createElement('div');
            errorMessage.setAttribute('id', 'error-message');
            errorMessage.innerText = `Error: ${error.message}`;
            errorMessage.style.color = 'red';
            outputContainer.appendChild(errorMessage);
            outputContainer.style.display = 'flex'; // Ensure the container is visible
        });
    });

    // Add smooth scroll functionality to the contact button
    document.querySelector('.navbar_btn a').addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default link behavior
        document.getElementById('contact').scrollIntoView({ behavior: 'smooth' });
    });

    // Add smooth scroll functionality to the project summary button
    document.querySelector('.navbar_links').addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default link behavior
        document.getElementById('servicesSection').scrollIntoView({ behavior: 'smooth' });
    });

    // New card flipping functionality
    document.querySelectorAll('.card_inner_a, .card_inner_b, .card_inner_c').forEach(card => {
        card.addEventListener('click', function () {
            card.classList.toggle('is-flipped');
        });
    });
});


