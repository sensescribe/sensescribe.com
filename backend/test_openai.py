import os
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Access environment variables
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def generate_speech(text, voice='alloy'):
    try:
        response = client.audio.speech.create(model="tts-1", voice=voice, input=text)
        audio_path = Path('../static/output_audio.mp3')
        with open(audio_path, 'wb') as f:
            f.write(response.content)
        logger.info("Audio file generated and saved as %s", audio_path)
        return '/static/output_audio.mp3'
    except Exception as e:
        logger.error(f"An error occurred during speech generation: {e}")
        return None
    
def generate_example_description(book_title):
    try:
        response = client.chat.completions.create(
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
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
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
        response = client.images.generate(
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

def generate_music_prompt(text, music_genre='classical'):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are an assistant that helps select real instrumental {music_genre} songs suitable for the specific scene described in the following text. Ensure that both the track and artist are real, verifiable, and popular. Provide the result in the format: track:<track> artist:<artist>."},
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
        response = client.chat.completions.create(
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
    scene_description = generate_prompt_for_image(text)
    if scene_description:
        generate_image(scene_description)
