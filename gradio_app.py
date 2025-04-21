import os
import gradio as gr
from pydub import AudioSegment

from bot_brain import encode_image, analyzing_image_with_query
from user_voice import recording_audio, transcribe_with_groq
from bot_voice import text_to_speech_with_elevenlabs


system_prompt="""You have to act as a professional doctor, i know you are not but this is for a chatbot. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""

def convert_mp3_to_wav(mp3_path, wav_path):
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")

def process_inputs(audio_filepath, image_filepath):
    speech_to_text_output = transcribe_with_groq(GROQ_API_KEY=os.environ.get("GROQ_API_KEY"), 
                                                 audio_filepath=audio_filepath,
                                                 stt_model="whisper-large-v3")

    if image_filepath:
        doctor_response = analyzing_image_with_query(query=system_prompt+speech_to_text_output, encoded_image=encode_image(image_filepath), model="llama-3.2-11b-vision-preview")
    else:
        doctor_response = "No image provided for me to analyze"

    mp3_path = "final.mp3"
    wav_path = "final.wav"
    text_to_speech_with_elevenlabs(input_text=doctor_response, output_filepath=mp3_path)
    convert_mp3_to_wav(mp3_path, wav_path)

    return speech_to_text_output, doctor_response, wav_path

iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath"),
        gr.Image(type="filepath")
    ],
    outputs=[
        gr.Textbox(label="Speech to Text"),
        gr.Textbox(label="Bot's Response"),
        gr.Audio("final.wav")
    ],
    title="AidBot"
)

iface.launch(debug=True)


