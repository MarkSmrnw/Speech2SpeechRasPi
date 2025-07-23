import os
import time
import threading

import numpy as np
import soundfile as sf
import sounddevice as sd

class record:
    def __init__(self, folder="AudioFiles"):

        print("Recorder ok.")

        self.audiofolder = folder

        self.isRecording = False
        self.recording_data = []
        self.sample_rate = 16000
        self.channels = 1
        self.recording_thread = None
        
    def checkRecordings(self):
        """- True = Successful
        - False = Failed"""
        try:
            print("Checking recording folder...")
            parentPath = os.path.abspath(os.path.dirname(__file__))
            audioPath = os.path.join(parentPath, self.audiofolder)

            os.makedirs(audioPath, exist_ok=True)
            files = os.listdir(audioPath)
            for i in range(0, len(files)):
                print(f"Found {files[i]}. Removing...")
                os.remove(os.path.join(audioPath, files[i]))
                print("Removed.")

            return True


        except Exception as E:
            print(f"Check Recordings returned an Error! {str(E)}")
            return False
        
    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Audio callback status: {status}")

        if self.isRecording:
            self.recording_data.append(indata.copy())
        
    def startRecording(self):
        if self.isRecording:
            print("Already recording.")
            return False
        
        try:
            print("Starting recording...")

            if not self.checkRecordings():
                print("Check returned false. Aborting...")
                return

            self.isRecording = True
            self.recording_data = []

            def record_audio():
                with sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    callback=self._audio_callback,
                    dtype=np.float32
                ):
                    while self.isRecording:
                        sd.sleep(100)

            self.recording_thread = threading.Thread(target=record_audio)
            self.recording_thread.start()
            
            print("Recording started.")
            return True
        except Exception as E:
            print(f"Error starting recording: {str(E)}")
            return False

    def stopRecording(self):
        if not self.isRecording:
            print("Not currently recording.")
            return False
        
        try:
            print("Stopping recording...")
            self.isRecording = False

            if self.recording_thread:
                self.recording_thread.join()

            if not self.recording_data:
                print("No recording data.")
                return False
            
            audio_data = np.concatenate(self.recording_data, axis=0)
            parentPath = os.path.abspath(os.path.dirname(__file__))
            audioPath = os.path.join(parentPath, self.audiofolder)
            filepath = os.path.join(audioPath, "latest.ogg")

            sf.write(filepath, audio_data, self.sample_rate, format="OGG")

            print("Recording stopped and saved.")

            return True
        except Exception as E:
            print(f"Error stopping recording: {str(E)}")
        
if __name__ == "__main__":
    recorder = record()

    print("STARTING IN...")
    for i in range(0, 4):
        time.sleep(1)
        print(3-i)

    print("STARTING!")

    recorder.startRecording()
    time.sleep(5)
    recorder.stopRecording()