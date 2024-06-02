from openai import OpenAI
import os

# Initialize OpenAI API client
client = OpenAI(
    api_key='sk-proj-Fv1JowqfU4g58ry9fi9jT3BlbkFJcEGJfYro8xpZUrEduk1G'
)

# Text examples and corresponding voice names
examples = {
    "alloy": "To be, or not to be, that is the question.",
    "echo": "It was the best of times, it was the worst of times.",
    "fable": "All animals are equal, but some animals are more equal than others.",
    "onyx": "Though I walk through the valley of the shadow of death, I will fear no evil; for You are with me; Your rod and Your staff, they comfort me.",
    "nova": "In the beginning, God created the heavens and the earth.",
    "shimmer": "The only thing we have to fear is fear itself."
}

# Directory to save the audio files
output_dir = "static/audio_samples"
os.makedirs(output_dir, exist_ok=True)

# Function to generate and save TTS audio
def generate_and_save_tts(text, voice_name):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            input=text,
            voice=voice_name
        )
        audio_path = os.path.join(output_dir, f"{voice_name}.mp3")
        with open(audio_path, 'wb') as f:
            f.write(response.content)
        print(f"Audio file for {voice_name} saved as {audio_path}")
    except Exception as e:
        print(f"An error occurred while generating audio for {voice_name}: {e}")

# Generate and save audio for each example
for voice, text in examples.items():
    generate_and_save_tts(text, voice)
