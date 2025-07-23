import os
import torch
import librosa

import soundfile as sf
import numpy as np

from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq

model_id = "openai/whisper-base" 

print(f"Loading processor for {model_id}...")
processor = AutoProcessor.from_pretrained(model_id)
print("Processor loaded.")

print(f"Loading model for {model_id}")
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id,
    torch_dtype="auto",
    device_map="auto"
)

def transcribe_audiofile(source, sampling_rate=16000, language="de", task="transcribe"):

    speech_array, original_sampling_rate = sf.read(source)

    if speech_array.ndim > 1: # Wenn Stereo...
        speech_array = speech_array.mean(axis=1) # Ersten Channel von Stereo

    if original_sampling_rate != sampling_rate: # Wenn die Samplingrates nicht übereinstimmen...
        print("Resampling audio to target rate...")

        speech_array = librosa.resample(
            y=speech_array,
            orig_sr=original_sampling_rate,
            target_sr=sampling_rate
        )

    print("Audio loaded.")

    inputs = processor(
        audio=speech_array,
        sampling_rate=sampling_rate,
        return_tensors="pt"
    ).to(model.device)

    print("Performing interface...")

    #model.disable_talker() # Kein sprechen, nur text. Schaltet den talker aus.

    generated_ids = model.generate(
        inputs["input_features"],
        language=language,
        task=task
    )

    transcribed_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    print("Transcribe complete.")
    return transcribed_text

def transcribe_audio(self):
    try:
        print(f"Starting transcription of: {self.file_path.get()}")
        print(f"File size: {os.path.getsize(self.file_path.get())} bytes")
        
        result = transcribe_audiofile(
            self.file_path.get(),
            language=self.language.get()
        )
        
        self.root.after(0, self.transcription_complete, result)
        
    except Exception as e:
        print(f"Transcription error: {e}")
        import traceback
        traceback.print_exc()
        self.root.after(0, self.transcription_error, str(e))

if __name__ == "__main__":
    AUDIO_PATH = r"C:\Users\goes1\OneDrive\Dokumente\GitHub\OpencampusSHPi\OpencampusSHPiProject\WhatsApp Ptt 2025-07-16 at 13.49.23.ogg"

    if os.path.exists(AUDIO_PATH):
        print("Path exsists")

        text = transcribe_audiofile(AUDIO_PATH)
        print()
        print(text)
        print()
        print("Done!")