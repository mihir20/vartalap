import argparse
import os
import torch
import whisper


def transcribe_audio(audio_file_path, model_name="base"):
    """
    Transcribe an audio file to text using OpenAI's Whisper model locally.

    Args:
        audio_file_path (str): Path to the audio file
        model_name (str): Whisper model size ('tiny', 'base', 'small', 'medium', 'large')

    Returns:
        str: Transcribed text
    """
    # Check if file exists
    if not os.path.exists(audio_file_path):
        return f"Error: File '{audio_file_path}' not found"

    try:
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")

        # Load the Whisper model
        print(f"Loading Whisper model: {model_name}")
        model = whisper.load_model(model_name, device=device)

        # Transcribe audio
        print("Transcribing audio...")
        result = model.transcribe(audio_file_path)

        return result["text"]
    except Exception as e:
        return f"Error processing audio file: {e}"

if __name__ == "__main__":
    # Transcribe the audio
    transcription = transcribe_audio('recording.wav', 'large')

    # Print or save the transcription
    if True:
        with open('summary.txt', 'w', encoding='utf-8') as f:
            f.write(transcription)
        print(f"Transcription saved")
    else:
        print("\nTranscription:")
        print(transcription)