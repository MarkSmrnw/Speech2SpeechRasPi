import subprocess
import piper
import wave
import io
import os

class GermanTTS:
    def __init__(self, model_path=None):
        if model_path is None:
            self.model_path = "de_DE-thorsten-medium.onnx"
        else:
            self.model_path = model_path

        self.voice = None
        self._load_model()
        
    def _load_model(self):
        try:
            # Check if the model file exists in the current directory or Voices subdirectory
            model_paths = [
                self.model_path,
                os.path.join("Voices", self.model_path),
                os.path.join(os.path.dirname(__file__), self.model_path),
                os.path.join(os.path.dirname(__file__), "Voices", self.model_path)
            ]
            
            model_found = False
            for path in model_paths:
                if os.path.exists(path):
                    print(f"Found model at: {path}")
                    self.model_path = path
                    model_found = True
                    break
            
            if not model_found:
                print("Model not found in any of the expected locations:")
                for path in model_paths:
                    print(f"  - {path}")
                print("Have you downloaded de_DE-thorsten-medium?")
                return
                
            self.voice = piper.PiperVoice.load(self.model_path)
            print(f"TTS model loaded successfully")
            
        except Exception as E:
            print(f"Error loading model: {E}")
            self.voice = None

    def speak(self, text, output_file="output.wav", play_audio=True):
        if not self.voice:
            print("No model loaded.")
            return False
        
        try:
            print(f"Synthesizing text: '{text}'")
            
            # Piper's synthesize method returns an iterator of AudioChunk objects
            # We need to extract the audio data from each AudioChunk
            
            audio_chunks = []
            sample_rate = None
            sample_channels = None
            sample_width = None
            
            # The synthesize method yields AudioChunk objects
            for audio_chunk in self.voice.synthesize(text):
                # Use the audio_int16_bytes attribute which contains the PCM data
                if hasattr(audio_chunk, 'audio_int16_bytes'):
                    audio_data = audio_chunk.audio_int16_bytes
                    audio_chunks.append(audio_data)
                    
                    # Get audio format info from the first chunk
                    if sample_rate is None:
                        sample_rate = audio_chunk.sample_rate
                        sample_channels = audio_chunk.sample_channels
                        sample_width = audio_chunk.sample_width
                        print(f"Audio format: {sample_rate}Hz, {sample_channels} channels, {sample_width} bytes per sample")
                else:
                    print("AudioChunk doesn't have audio_int16_bytes attribute")
            
            if not audio_chunks:
                print("Error: No audio chunks generated")
                return False
            
            # Combine all audio chunks
            audio_data = b''.join(audio_chunks)
            print(f"Combined audio data: {len(audio_data)} bytes")
            
            if len(audio_data) == 0:
                print("Error: No audio data in chunks")
                return False
            
            # Create WAV file with the audio data
            with wave.open(output_file, 'wb') as wav_file:
                # Set WAV parameters from AudioChunk info
                wav_file.setnchannels(sample_channels or 1)  # Use from AudioChunk or default to mono
                wav_file.setsampwidth(sample_width or 2)     # Use from AudioChunk or default to 16-bit
                wav_file.setframerate(sample_rate or 22050)  # Use from AudioChunk or default
                
                # Write the audio data
                wav_file.writeframes(audio_data)
            
            # Check if file was created and has content
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"Saved audio file: {output_file} ({file_size} bytes)")
                
                if file_size <= 44:  # WAV header is 44 bytes
                    print("Warning: Generated audio file appears to be empty (only header)")
                    return False
                else:
                    print("Audio file generated successfully!")
            else:
                print("Error: Audio file was not created")
                return False

            if play_audio:
                self.play_audio(output_file)
                
            return True
            
        except Exception as E:
            print(f"Error generating speech: {E}")
            import traceback
            traceback.print_exc()
            return False

    def play_audio(self, audio_file):
        try:
            import platform
            system = platform.system()
            
            if system == "Windows":
                os.startfile(audio_file)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", audio_file], check=True)
            elif system == "Linux":
                # Try different audio players commonly available on Linux
                players = ["aplay", "paplay", "mpv", "vlc", "mplayer", "play"]
                
                for player in players:
                    try:
                        # Check if the player is available
                        subprocess.run(["which", player], check=True, 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        # If available, use it to play the audio
                        subprocess.run([player, audio_file], check=True)
                        print(f"Playing audio with {player}")
                        return
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                
                # If no player found, try xdg-open as fallback
                try:
                    subprocess.run(["xdg-open", audio_file], check=True)
                    print("Playing audio with default application")
                except subprocess.CalledProcessError:
                    print("No suitable audio player found. Please install aplay, mpv, vlc, or another audio player.")
            else:
                print(f"Unsupported operating system: {system}")
                
        except Exception as E:
            print(f"Error playing audio: {E}")

if __name__ == "__main__":
    tts = GermanTTS(model_path="Voices/de_DE-thorsten-medium.onnx")
    tts.speak("das ist ein test, hallo wie gehts", play_audio=True)