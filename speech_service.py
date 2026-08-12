import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()


def transcribe_audio(audio_file):
    speech_key = os.getenv("SPEECH_KEY")
    speech_region = os.getenv("SPEECH_REGION")

    if not speech_key or not speech_region:
        raise ValueError("Azure Speech credentials are missing.")

    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key,
        region=speech_region
    )

    speech_config.speech_recognition_language = "en-US"

    audio_config = speechsdk.audio.AudioConfig(
        filename=audio_file
    )

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text

    elif result.reason == speechsdk.ResultReason.NoMatch:
        return "No speech could be recognized."

    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        raise Exception(
            f"Speech recognition canceled: {cancellation.reason}. "
            f"Details: {cancellation.error_details}"
        )

    return "Unable to recognize speech."