
document.addEventListener('DOMContentLoaded', function() {
    const voiceSelect = document.getElementById('voiceSelect');
    const artStyleSelect = document.getElementById('artStyleSelect');
    const musicGenreSelect = document.getElementById('musicGenreSelect');
    const generateButton = document.getElementById('generateButton');
    const voiceExamplePlayer = document.getElementById('voiceExamplePlayer');
    const generatedAudioPlayer = document.getElementById('generatedAudioPlayer');
    const generatedVideoPlayer = document.getElementById('generatedVideoPlayer');
    const outputContainer = document.getElementsByClassName('outputContainer')[0];
    const loadingBar = document.getElementById('loadingBar');
    const outputImage = document.getElementById('outputImage');
    const bookTitleInput = document.getElementById('bookTitleInput');
    const generateExampleButton = document.getElementById('generateExampleButton');
    const textInput = document.getElementById('textInput');
    const shareButtons = document.querySelector('.share-buttons');
    const downloadVButton = document.getElementById('downloadVButton');
    const downloadAButton = document.getElementById('downloadAButton');
    const shareX = document.getElementById('shareX');

    const voiceSamples = {
        "alloy": "/static/static/audio_samples/alloy.mp3",
        "Antoni": "/static/static/audio_samples/Antoni.mp3",
        "Arnold": "/static/static/audio_samples/Arnold.mp3",
        "Callum": "/static/static/audio_samples/Callum.mp3",
        "Charlie": "/static/static/audio_samples/Charlie.mp3",
        "Charlotte": "/static/static/audio_samples/Charlotte.mp3",
        "Clyde": "/static/static/audio_samples/Clyde.mp3",
        "Dave": "/static/static/audio_samples/Dave.mp3",
        "Domi": "/static/static/audio_samples/Domi.mp3",
        "Dorothy": "/static/static/audio_samples/Dorothy.mp3",
        "Drew": "/static/static/audio_samples/Drew.mp3",
        "echo": "/static/static/audio_samples/echo.mp3",
        "Elli": "/static/static/audio_samples/Elli.mp3",
        "Emily": "/static/static/audio_samples/Emily.mp3",
        "fable": "/static/static/audio_samples/fable.mp3",
        "Fin": "/static/static/audio_samples/Fin.mp3",
        "George": "/static/static/audio_samples/George.mp3",
        "Harry": "/static/static/audio_samples/Harry.mp3",
        "James": "/static/static/audio_samples/James.mp3",
        "Jeremy": "/static/static/audio_samples/Jeremy.mp3",
        "Joseph": "/static/static/audio_samples/Joseph.mp3",
        "Josh": "/static/static/audio_samples/Josh.mp3",
        "Liam": "/static/static/audio_samples/Liam.mp3",
        "Matilda": "/static/static/audio_samples/Matilda.mp3",
        "Michael": "/static/static/audio_samples/Michael.mp3",
        "nova": "/static/static/audio_samples/nova.mp3",
        "onyx": "/static/static/audio_samples/onyx.mp3",
        "Patrick": "/static/static/audio_samples/Patrick.mp3",
        "Paul": "/static/static/audio_samples/Paul.mp3",
        "Rachel": "/static/static/audio_samples/Rachel.mp3",
        "Sarah": "/static/static/audio_samples/Sarah.mp3",
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

    generateExampleButton.addEventListener('click', function() {
        const bookTitle = bookTitleInput.value;

        textInput.value = "Generating example, please wait...";

        fetch('/generate_example', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ bookTitle: bookTitle })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            textInput.value = data.exampleDescription;

            textInput.scrollIntoView({ behavior: 'smooth', block: 'start' });
            document.body.style.zoom = 1.0; 
        })
        .catch(error => {
            console.error('Error:', error);
            textInput.value = "Failed to generate example. Please try again.";
        });
    });

    generateButton.addEventListener('click', function() {
        shareButtons.style.display = 'none';

        const textInputValue = textInput.value;
        const selectedVoice = voiceSelect.value;
        const selectedArtStyle = artStyleSelect.value;
        const selectedMusicGenre = musicGenreSelect.value;

        const previousError = document.getElementById('error-message');
        if (previousError) {
            previousError.remove();
        }

        outputContainer.style.display = 'flex';
        loadingBar.style.width = '0%';
        loadingBar.innerText = 'Loading...';

        generatedAudioPlayer.style.display = 'none';
        generatedVideoPlayer.style.display = 'none';
        outputImage.style.display = 'none';
        loadingBar.innerText = 'Loading...';
        loadingBar.style.display = 'block';
        generatedAudioPlayer.src = '';
        generatedVideoPlayer.src = '';
        outputImage.src = '';

        const offset = outputContainer.getBoundingClientRect().top + window.scrollY - (window.innerHeight / 2) + (loadingBar.offsetHeight / 2);
        window.scrollTo({ top: offset, behavior: 'smooth' });

        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: textInputValue,
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
            if (data.audioUrl && data.imageUrl && data.videoUrl) {
                loadingBar.style.width = '100%';
                loadingBar.innerText = 'Complete';
                setTimeout(() => {
                    generatedAudioPlayer.src = data.audioUrl;
                    outputImage.src = data.imageUrl;
                    generatedVideoPlayer.src = data.videoUrl;
                    generatedAudioPlayer.style.display = 'block';
                    outputImage.style.display = 'block';
                    generatedVideoPlayer.style.display = 'block';
                    loadingBar.style.display = 'none';
                    shareButtons.style.display = 'flex';
                    setupShareButtons(data.videoUrl, data.audioUrl);
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

            const errorMessage = document.createElement('div');
            errorMessage.setAttribute('id', 'error-message');
            errorMessage.innerText = `Error: ${error.message}`;
            errorMessage.style.color = 'red';
            outputContainer.appendChild(errorMessage);
            outputContainer.style.display = 'flex';
        });
    });

    function setupShareButtons(videoUrl, audioUrl) {
        const downloadVButton = document.getElementById('downloadVButton');
        const downloadAButton = document.getElementById('downloadAButton');
        const shareX = document.getElementById('shareX');
    
        downloadVButton.href = videoUrl;
        downloadVButton.download = 'sensescribe_output.mp4';

        downloadAButton.href = audioUrl;
        downloadAButton.download = 'sensescribe_output.mp3';
        
        const encodedUrl = encodeURIComponent(videoUrl);
        const XShareUrl = `https://X.com/intent/tweet?text=Check out my creation on Sensescribe!&url=${encodedUrl}`;
        shareX.href = XShareUrl;

        const generatedVideoPlayer = document.getElementById('generatedVideoPlayer');
        generatedVideoPlayer.style.display = 'none';
    }
    

    document.querySelector('.navbar_btn a').addEventListener('click', function(event) {
        event.preventDefault();
        document.getElementById('contact').scrollIntoView({ behavior: 'smooth' });
    });

    document.querySelector('.navbar_links').addEventListener('click', function(event) {
        event.preventDefault();
        document.getElementById('servicesSection').scrollIntoView({ behavior: 'smooth' });
    });

    document.querySelectorAll('.card_inner_a, .card_inner_b, .card_inner_c').forEach(card => {
        card.addEventListener('click', function () {
            card.classList.toggle('is-flipped');
        });
    });
});
