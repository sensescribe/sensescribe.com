import os
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import test_openai  
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from pydub import AudioSegment
import time
import subprocess

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__, static_folder='../static', static_url_path='/static', template_folder='../templates')

# Set up Spotify API credentials

spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

# Cache for the Spotify token
spotify_token_cache = {
    'token': None,
    'expires_at': 0
}

def get_spotify_token():
    token_url = "https://accounts.spotify.com/api/token"
    token_data = {
        'grant_type': 'client_credentials'
    }
    token_headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        token_response = requests.post(token_url, data=token_data, headers=token_headers, auth=(spotify_client_id, spotify_client_secret))
        token_response.raise_for_status()
        token_info = token_response.json()
        token = token_info['access_token']
        expires_in = token_info['expires_in']  # Token lifetime in seconds
        expires_at = time.time() + expires_in  # Calculate the expiry time
        logger.info(f"Spotify token generated: {token} (expires in {expires_in} seconds)")
        return token, expires_at
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get token: {e}")
        raise
    
def get_valid_spotify_token():
    global spotify_token_cache
    if spotify_token_cache['token'] is None or time.time() >= spotify_token_cache['expires_at']:
        spotify_token_cache['token'], spotify_token_cache['expires_at'] = get_spotify_token()
    return spotify_token_cache['token']

def search_spotify_for_track(track_description, music_genre, retries=3):
    token = get_valid_spotify_token()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    for attempt in range(retries):
        try:
            response = requests.get(
                "https://api.spotify.com/v1/search",
                headers=headers,
                params={
                    'q': track_description,
                    'limit': 1,
                    'type': 'track'
                }
            )
            response_data = response.json()
            if 'tracks' in response_data and response_data['tracks']['items']:
                track = response_data['tracks']['items'][0]
                if track['preview_url']:
                    return track['preview_url']
                else:
                    logger.warning(f"Track found but no preview URL. Retrying ({attempt + 1}/{retries})...")
            else:
                logger.warning(f"No tracks found on attempt {attempt + 1}/{retries}. Retrying...")
            feedback = f"The last suggestion '{track_description}' did not have a preview URL. Please suggest another track in the {music_genre} genre, and ensure that both the track and artist are real, verifiable, and popular"
            track_description = test_openai.generate_music_prompt_with_feedback(track_description, feedback, music_genre)
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred during Spotify search: {e}")
            continue
    return None

def combine_audio(tts_path=None, music_url=None, sfx_path=None):
    try:
        combined_audio = None

        # Load TTS audio if available
        if tts_path:
            tts_audio = AudioSegment.from_file(tts_path)
            combined_audio = tts_audio

        # Load background music if available
        if music_url:
            music_response = requests.get(music_url)
            music_response.raise_for_status()
            music_path = '../static/background_music.mp3'
            with open(music_path, 'wb') as f:
                f.write(music_response.content)
            logger.info(f"Music downloaded and saved to {music_path}")
            background_music = AudioSegment.from_file(music_path)
            background_music = background_music - 19  # Reduce volume

            if combined_audio:
                while len(background_music) < len(combined_audio):
                    background_music += background_music
                background_music = background_music[:len(combined_audio)]
                combined_audio = combined_audio.overlay(background_music)
            else:
                combined_audio = background_music

        # Load sound effects if available
        if sfx_path:
            sound_effects = AudioSegment.from_file(sfx_path)
            sound_effects = sound_effects - 5  # Adjust volume for sound effects

            if combined_audio:
                while len(sound_effects) < len(combined_audio):
                    sound_effects += sound_effects
                sound_effects = sound_effects[:len(combined_audio)]
                combined_audio = combined_audio.overlay(sound_effects)
            else:
                combined_audio = sound_effects

        if not combined_audio:
            logger.error("No audio sources available to combine.")
            return None, None

        combined_audio_path = '../static/combined_audio.mp3'
        combined_audio.export(combined_audio_path, format="mp3")
        logger.info(f"Combined audio saved to {combined_audio_path}")

        return '/static/combined_audio.mp3', None
    except Exception as e:
        logger.error(f"An error occurred while combining audio: {e}")
        return None, None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_example', methods=['POST'])
def generate_example():
    data = request.get_json()
    book_title = data['bookTitle']

    example_description = test_openai.generate_example_description(book_title)
    if not example_description:
        return jsonify({'error': 'Failed to generate example description'}), 500

    return jsonify({'exampleDescription': example_description})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    text = data['text']
    voice = data.get('voice', 'none')
    art_style = data.get('artStyle', 'none')
    music_genre = data.get('musicGenre', 'none')
    include_sound_effects = data.get('includeSoundEffects', False)
    
    if voice == 'none' and art_style == 'none' and music_genre == 'none' and not include_sound_effects:
        return jsonify({'error': 'Please select at least one option.'}), 400

    # Paths for generated files
    tts_audio_path = '../static/output_audio.mp3'
    background_music_path = '../static/background_music.mp3'
    sfx_audio_path = '../static/fx_audio_elevenlabs.mp3'
    combined_audio_path = '../static/combined_audio.mp3'
    image_path = '../static/output_image.png'

    # Clear previous files
    for path in [tts_audio_path, background_music_path, sfx_audio_path, combined_audio_path, image_path]:
        if os.path.exists(path):
            os.remove(path)

    # Generate TTS audio
    tts_audio_url = None
    if voice != 'none':
        tts_audio_url = test_openai.generate_speech(text, voice)
        if not tts_audio_url:
            return jsonify({'error': 'Failed to generate audio'}), 500

    # Generate image
    image_url = None
    if art_style != 'none':
        scene_description = test_openai.generate_prompt_for_image(text, art_style)
        if not scene_description:
            return jsonify({'error': 'Failed to generate scene description'}), 500

        image_url = test_openai.generate_image(scene_description)
        if not image_url:
            return jsonify({'error': 'Failed to generate image'}), 500

        try:
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            with open(image_path, 'wb') as f:
                f.write(image_response.content)
        except Exception as e:
            return jsonify({'error': 'Failed to download image'}), 500

    # Generate music
    music_url = None
    if music_genre != 'none':
        music_description = test_openai.generate_music_prompt(text, music_genre)
        logger.info(f"Generated music description: {music_description}")
        if not music_description:
            return jsonify({'error': 'Failed to generate music description'}), 500

        try:
            token = get_valid_spotify_token()
        except Exception as e:
            return jsonify({'error': f'Failed to get Spotify token: {e}'}), 500

        music_url = search_spotify_for_track(music_description, music_genre)
        if not music_url:
            return jsonify({'error': 'Failed to find a suitable music track'}), 500

    # Generate sound effects
    sfx_audio_url = None
    if include_sound_effects:
        soundfx_prompt = test_openai.generate_soundfx_prompt(text)
        if not soundfx_prompt:
            return jsonify({'error': 'Failed to generate sound effects prompt'}), 500

        sfx_audio_url = test_openai.generate_sound_effect(soundfx_prompt)
        if not sfx_audio_url:
            return jsonify({'error': 'Failed to generate sound effects'}), 500

    # Combine audio
    combined_audio_url = None
    if voice != 'none' or music_url or include_sound_effects:
        combined_audio_url, _ = combine_audio(
            tts_path=tts_audio_path if voice != 'none' else None,
            music_url=music_url,
            sfx_path=sfx_audio_path if include_sound_effects else None
        )
        if not combined_audio_url:
            return jsonify({'error': 'Failed to combine audio'}), 500

    # Generate full URLs for sharing
    base_url = request.url_root.rstrip('/')
    full_audio_url = f"{base_url}/static/combined_audio.mp3" if combined_audio_url else None
    full_image_url = f"{base_url}/static/output_image.png" if image_url else None

    return jsonify({'audioUrl': full_audio_url, 'imageUrl': full_image_url})



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
