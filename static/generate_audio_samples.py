from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import save
import os

# Initialize OpenAI API client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize ElevenLabs API client
elevenlabs_client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))

# Text examples and corresponding voice names
'''openai_examples = {
    "alloy": "To be, or not to be, that is the question.",
    "echo": "It was the best of times, it was the worst of times.",
    "fable": "All animals are equal, but some animals are more equal than others.",
    "onyx": "Though I walk through the valley of the shadow of death, I will fear no evil.",
    "nova": "In the beginning, God created the heavens and the earth.",
    "shimmer": "The only thing we have to fear is fear itself."
}'''

''' "Rachel": {"id": "21m00Tcm4TlvDq8ikWAM", "text": "The quick brown fox jumps over the lazy dog."},
    "Drew": {"id": "29vD33N1CtxCmqQRPOHJ", "text": "A journey of a thousand miles begins with a single step."},
    "Clyde": {"id": "2EiwWnXFnvU5JabPnv8n", "text": "To be yourself in a world that is constantly trying to make you something else is the greatest accomplishment."},
    "Paul": {"id": "5Q0t7uMcjvnagumLfvZi", "text": "Life is what happens when you're busy making other plans."},
    "Domi": {"id": "AZnzlk1XvdvUeBnXmlld", "text": "You only live once, but if you do it right, once is enough."},
    "Dave": {"id": "CYw3kZ02Hs0563khs1Fj", "text": "The purpose of our lives is to be happy."},
    "Fin": {"id": "D38z5RcWu1voky8WS1ja", "text": "Get busy living or get busy dying."},
    "Sarah": {"id": "EXAVITQu4vr4xnSDxMaL", "text": "Many of life's failures are people who did not realize how close they were to success when they gave up."},
    "Antoni": {"id": "ErXwobaYiN019PkySvjV", "text": "If you want to live a happy life, tie it to a goal, not to people or things."},
    "Thomas": {"id": "GBv7mTt0atIp3Br8iCZE", "text": "Never let the fear of striking out keep you from playing the game."},
    "Charlie": {"id": "IKne3meq5aSn9XLyUdCD", "text": "Money and success don't change people; they merely amplify what is already there."},
    "George": {"id": "JBFqnCBsd6RMkjVDRZzb", "text": "Your time is limited, so don't waste it living someone else's life."},
    "Emily": {"id": "LcfcDJNUP1GQjkzn1xUU", "text": "Not how long, but how well you have lived is the main thing."},
    "Elli": {"id": "MF3mGyEYCl7XYWbV9V6O", "text": "If life were predictable it would cease to be life, and be without flavor."},
    "Callum": {"id": "N2lVS1w4EtoT3dr4eOWO", "text": "The whole secret of a successful life is to find out what is one's destiny to do, and then do it."},
    "Patrick": {"id": "ODq5zmih8GrVes37Dizd", "text": "In order to write about life first you must live it."},
    "Harry": {"id": "SOYHLrjzK2X1ezoPC6cr", "text": "The big lesson in life, baby, is never be scared of anyone or anything."},'''

# Text examples and corresponding voice IDs for ElevenLabs
elevenlabs_examples = {
    "James": {"id": "ZQe5CZNOzWyzPSCn5a3c", "text": "Everything negative, pressure, challenges, is all an opportunity for me to rise."},
}
'''elevenlabs_examples = {
    "Harry": {"id": "SOYHLrjzK2X1ezoPC6cr", "text": "The big lesson in life, baby, is never be scared of anyone or anything."},
    "Liam": {"id": "TX3LPaxmHKxFdv7VOQHJ", "text": "Curiosity about life in all of its aspects, I think, is still the secret of great creative people."},
    "Dorothy": {"id": "ThT5KcBeYPX3keUQqHPh", "text": "Life is not a problem to be solved, but a reality to be experienced."},
    "Josh": {"id": "TxGEqnHWrfWFTfGW9XjX", "text": "The unexamined life is not worth living."},
    "Arnold": {"id": "VR6AewLTigWG4xSOukaG", "text": "Turn your wounds into wisdom."},
    "Charlotte": {"id": "XB0fDUnXU5powFXDhCwa", "text": "The way I see it, if you want the rainbow, you gotta put up with the rain."},
    "Alice": {"id": "Xb7hH8MSUJpSbSDYk0k2", "text": "Do all the good you can, for all the people you can, in all the ways you can, as long as you can."},
    "Matilda": {"id": "XrExE9yKIg1WjnnlVkGX", "text": "Don't settle for what life gives you; make life better and build something."},
    "James": {"id": "ZQe5CZNOzWyzPSCn5a3c", "text": "Everything negative, pressure, challenges, is all an opportunity for me to rise."},
    "Joseph": {"id": "Zlb1dXrM653N07WRdFW3", "text": "I like criticism. It makes you strong."},
    "Jeremy": {"id": "bVMeCyTHy58xNoL34h3p", "text": "You never really learn much from hearing yourself speak."},
    "Michael": {"id": "flq6f7yk4E4fJM5XTYuZ", "text": "Life imposes things on you that you can't control, but you still have the choice of how you're going to live through it."}
}'''
''' "Ethan": {"id": "g5CIjZEefAph4nQFvHAz", "text": "Live for each second without hesitation."},
    "Chris": {"id": "iP95p4xoKVk53GoZ742B", "text": "Life is like riding a bicycle. To keep your balance, you must keep moving."},
    "Gigi": {"id": "jBpfuIE2acCO8z3wKNLl", "text": "The greatest glory in living lies not in never falling, but in rising every time we fall."},
    "Freya": {"id": "jsCqWAovK2LkecY7zXl4", "text": "The purpose of our lives is to be happy."},
    "Brian": {"id": "nPczCjzI2devNBz1zQrb", "text": "Life is really simple, but we insist on making it complicated."},
    "Grace": {"id": "oWAxZDx7w5VEj9dCyTzz", "text": "May you live all the days of your life."},
    "Daniel": {"id": "onwK4e9ZLuTAKqWW03F9", "text": "Success is not how high you have climbed, but how you make a positive difference to the world."},
    "Lily": {"id": "pFZP5JQG7iQjIQuC4Bku", "text": "In the end, it's not the years in your life that count. It's the life in your years."},
    "Serena": {"id": "pMsXgVXv3BLzUgSXRplE", "text": "You have within you right now, everything you need to deal with whatever the world can throw at you."},
    "Adam": {"id": "pNInz6obpgDQGcFmaJgB", "text": "Believe you can and you're halfway there."},
    "Nicole": {"id": "piTKgcLEGmPE4e6mEKli", "text": "The only impossible journey is the one you never begin."},
    "Bill": {"id": "pqHfZKP75CvOlQylNhV4", "text": "Life is what happens when you're busy making other plans."},
    "Jessie": {"id": "t0jbNlBVZ17f02VDIeMI", "text": "Don't judge each day by the harvest you reap but by the seeds that you plant."},
    "Sam": {"id": "yoZ06aMxZJJ28mfd3POQ", "text": "Go confidently in the direction of your dreams! Live the life you've imagined."},
    "Glinda": {"id": "z9fAnlkpzviPz146aGWa", "text": "The best way to predict your future is to create it."},
    "Giovanni": {"id": "zcAOhNBS3c14rBihAFp1", "text": "The future belongs to those who believe in the beauty of their dreams."},
    "Mimi": {"id": "zrHiDhphv9ZnVXBqCLjz", "text": "It does not matter how slowly you go as long as you do not stop."} '''



# Directory to save the audio files
output_dir = "static/audio_samples"
os.makedirs(output_dir, exist_ok=True)

# Function to generate and save TTS audio

'''def generate_and_save_tts_openai(text, voice_name):
    try:
        response = openai_client.audio.speech.create(
            model="tts-1",
            input=text,
            voice=voice_name
        )
        audio_path = os.path.join(output_dir, f"{voice_name}.mp3")
        with open(audio_path, 'wb') as f:
            f.write(response.content)
        print(f"Audio file for {voice_name} saved as {audio_path}")
    except Exception as e:
        print(f"An error occurred while generating audio for {voice_name}: {e}")'''

# Function to generate and save TTS audio for ElevenLabs
def generate_and_save_tts_elevenlabs(voice_id, text, voice_name):
    try:
        audio = elevenlabs_client.generate(
            text=text,
            voice=voice_id
        )
        audio_path = os.path.join(output_dir, f"{voice_name}.mp3")
        save(audio, audio_path)
        print(f"Audio file for {voice_name} saved as {audio_path}")
    except Exception as e:
        print(f"An error occurred while generating audio for {voice_name}: {e}")

# Generate and save audio for each OpenAI example
'''for voice, text in openai_examples.items():
    generate_and_save_tts_openai(text, voice)'''

# Generate and save audio for each ElevenLabs example
for voice_name, details in elevenlabs_examples.items():
    generate_and_save_tts_elevenlabs(details['id'], details['text'], voice_name)


