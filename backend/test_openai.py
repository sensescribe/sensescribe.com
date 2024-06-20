import os
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import logging
from elevenlabs.client import ElevenLabs
from elevenlabs import save

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Access environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=openai_api_key)

elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

elevenlabs_voices = {
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Drew": "29vD33N1CtxCmqQRPOHJ",
    "Clyde": "2EiwWnXFnvU5JabPnv8n",
    "Paul": "5Q0t7uMcjvnagumLfvZi", 
    "Domi": "AZnzlk1XvdvUeBnXmlld",
    "Dave": "CYw3kZ02Hs0563khs1Fj",
    "Fin": "D38z5RcWu1voky8WS1ja", 
    "Sarah": "EXAVITQu4vr4xnSDxMaL", 
    "Antoni": "ErXwobaYiN019PkySvjV", 
    "Charlie": "IKne3meq5aSn9XLyUdCD",
    "George": "JBFqnCBsd6RMkjVDRZzb", 
    "Emily": "LcfcDJNUP1GQjkzn1xUU", 
    "Elli": "MF3mGyEYCl7XYWbV9V6O", 
    "Callum": "N2lVS1w4EtoT3dr4eOWO", 
    "Patrick": "ODq5zmih8GrVes37Dizd", 
    "Harry": "SOYHLrjzK2X1ezoPC6cr", 
    "Liam": "TX3LPaxmHKxFdv7VOQHJ", 
    "Dorothy": "ThT5KcBeYPX3keUQqHPh", 
    "Josh": "TxGEqnHWrfWFTfGW9XjX", 
    "Arnold": "VR6AewLTigWG4xSOukaG", 
    "Charlotte": "XB0fDUnXU5powFXDhCwa", 
    "Matilda": "XrExE9yKIg1WjnnlVkGX",
    "James": "ZQe5CZNOzWyzPSCn5a3c",
    "Joseph": "Zlb1dXrM653N07WRdFW3", 
    "Jeremy": "bVMeCyTHy58xNoL34h3p",
    "Michael": "flq6f7yk4E4fJM5XTYuZ"
    }

openai_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

        
def generate_speech(text, voice='alloy'):
    try:
        if voice in openai_voices:
            response = openai_client.audio.speech.create(model="tts-1", voice=voice, input=text)
            audio_path = Path('../static/output_audio.mp3')
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            logger.info("Audio file generated and saved as %s", audio_path)
            return '/static/output_audio_openai.mp3'
        
        elif voice in elevenlabs_voices:
            voice_id = elevenlabs_voices[voice]
            audio = elevenlabs_client.generate(
                text=text,
                voice=voice_id
            )
            audio_path = Path('../static/output_audio.mp3')
            save(audio, str(audio_path))
            logger.info("Audio file generated and saved as %s", audio_path)
            return '/static/output_audio_elevenlabs.mp3'
        
        else:
            raise ValueError("Invalid voice selected")

    except Exception as e:
        logger.error(f"An error occurred during speech generation: {e}")
        return None

    
def generate_example_description(book_title):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You generate vivid scene descriptions from literature. You only generate an extract from the literature named, and say nothing else."},
                {"role": "user", "content": f"Generate an example of vivid scene description from '{book_title}'. It is important that you just return the extract and say nothing else."}
            ]
        )
        logger.debug("Full API Response: %s", response)
        example_description = response.choices[0].message.content.strip()
        return example_description
    except Exception as e:
        logger.error(f"An error occurred during example generation: {e}")
        return None


def generate_prompt_for_image(text, art_style='abstract'):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Translate the following text into a single brief sentence that describes a scene suitable for generating an image with DALL.E, and request it in the {art_style} style."},
                {"role": "user", "content": text}
            ]
        )
        logger.debug("Full API Response: %s", response)
        scene_description = response.choices[0].message.content.strip()
        return scene_description
    except Exception as e:
        logger.error(f"An error occurred during prompt generation: {e}")
        return None

def generate_image(scene_description):
    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=scene_description,
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url
        logger.info("Image generated and available at: %s", image_url)
        return image_url
    except Exception as e:
        logger.error(f"An error occurred during image generation: {e}")
        return None
    
def generate_soundfx_prompt(text):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are an assistant that translates text into a very short prompt for the elevenlabs text to sound effects API. describe a sound effect that complements the mood and context of the scene described by the text, and ensure the maximum length is a single sentence of a few words."},
                {"role": "user", "content": f"Translate the following text into a brief sound effects prompt: {text}"}
            ]
        )
        soundfx_prompt = response.choices[0].message.content.strip()
        return soundfx_prompt
    except Exception as e:
        logger.error(f"An error occurred during music prompt generation: {e}")
        return None
    
def generate_sound_effect(soundfx_prompt):
    try:
        result = elevenlabs_client.text_to_sound_effects.convert(
            text=soundfx_prompt,
            duration_seconds=10,  # Optional, if not provided will automatically determine the correct length
            prompt_influence=0.3,  # Optional, if not provided will use the default value of 0.3
        )
        audio_path = Path('../static/fx_audio_elevenlabs.mp3')
        with open(audio_path, "wb") as f:
            for chunk in result:
                f.write(chunk)
        logger.info("Sound effect generated and saved as %s", audio_path)
        return '/static/fx_audio_elevenlabs.mp3'
    except Exception as e:
        logger.error(f"An error occurred during sound effect generation: {e}")
        return None

def generate_music_prompt(text, music_genre='classical'):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are an assistant that helps select real instrumental {music_genre} songs suitable for the specific scene described in the following text. Search the web, and ensure that both the track and artist are real, verifiable, and popular. Provide the result in the format: track:<track> artist:<artist>."},
                {"role": "user", "content": text}
            ]
        )
        music_description = response.choices[0].message.content.strip()
        return music_description
    except Exception as e:
        logger.error(f"An error occurred during music prompt generation: {e}")
        return None

def generate_music_prompt_with_feedback(text, music_genre, feedback):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are an assistant that helps select real {music_genre} instrumental songs suitable for the specific scene described in the following text. Ensure that both the track and artist are real, verifiable, and popular. Provide the result in the format: track:<track> artist:<artist>. {feedback}"},
                {"role": "user", "content": text}
            ]
        )
        music_description = response.choices[0].message.content.strip()
        return music_description
    except Exception as e:
        logger.error(f"An error occurred during music prompt generation: {e}")
        return None

if __name__ == "__main__":
    text = "The quick brown fox jumps over the lazy dog."
    generate_speech(text)
    generate_speech(text, voice='alloy')
    generate_speech(text, voice='Rachel')
    scene_description = generate_prompt_for_image(text)
    if scene_description:
        generate_image(scene_description)
