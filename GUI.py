import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import threading
import os

from transcribe import transcribe_audiofile
from audioHandler import record as rec
from OllamaResponse import OllamaClient as OC
from tts import GermanTTS

class AudioTranscriberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech to Speech")
        self.root.geometry("600x700")

        self.automatic = False

        self.recorder = rec()
        self.recorder.checkRecordings()

        self.ollama_client = OC(temperature=1)
        
        # File selection
        file_frame = tk.Frame(root)
        file_frame.pack(pady=10)
        
        tk.Label(file_frame, text="Audio File:").pack(side=tk.LEFT)
        self.file_path = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.file_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT)
        
        # Language selection
        lang_frame = tk.Frame(root)
        lang_frame.pack(pady=10)

        self.automaticCheck = tk.Checkbutton(root, text="Automatic", onvalue=True, offvalue=False, command=self.automatic_command)
        self.automaticCheck.pack()

        #Recording area
        self.startrecbutton = tk.Button(root, text="Start recording", command=self.start_rec)
        self.stoprecbutton = tk.Button(root, text="Stop recording", command=self.stop_rec)

        self.stoprecbutton.config(state=tk.DISABLED)

        self.startrecbutton.pack(anchor=tk.W, padx=20, fill=tk.X)
        self.stoprecbutton.pack(anchor=tk.W, padx=20, fill=tk.X)
        
        tk.Label(lang_frame, text="Language:").pack(side=tk.LEFT)
        self.language = tk.StringVar(value="de")
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.language, 
                                  values=["de", "en", "fr", "es", "it"])
        lang_combo.pack(side=tk.LEFT, padx=5)
        
        # Transcribe button
        self.transcribe_btn = tk.Button(root, text="Transcribe Audio", 
                                       command=self.start_transcription)
        self.transcribe_btn.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.progress.pack(pady=10, fill=tk.X, padx=20)
        
        # Status label
        self.status_label = tk.Label(root, text="Ready")
        self.status_label.pack(pady=5)
        
        # Results text area
        tk.Label(root, text="Transcription Result:").pack(anchor=tk.W, padx=20)
        self.result_text = tk.Text(root, height=5, width=70)
        self.result_text.pack(anchor=tk.W, fill=tk.X, padx=20)

        self.sendToAi = tk.Button(root, text="Prompt A.I",
                                  command=self.generate_response, state=tk.DISABLED)
        self.sendToAi.pack(pady=5)

        tk.Label(root, text="A.I Response:").pack(anchor=tk.W, padx=20)
        self.ai_response = tk.Text(root, height=5, width=70)
        self.ai_response.pack(anchor=tk.W, fill=tk.X, padx=20)
        
        self.tts_button = ttk.Button(root, text="Make TTS file", command=self.doTTS)
        self.tts_button.pack(anchor=tk.W, fill=tk.X)
        self.tts_button_play = ttk.Button(root, text="Play TTS file")
        self.tts_button_play.pack(anchor=tk.W, fill=tk.X)
        
        # Save button
        self.save_btn = tk.Button(root, text="Save Transcription", 
                                 command=self.save_transcription, state=tk.DISABLED)
        self.save_btn.pack(pady=5)

    def doTTS(self):
        print("TTSing it")
        try:
            text = self.ai_response.get("1.0", tk.END).strip()
            print(text)

            tts = GermanTTS("Voices/de_DE-thorsten-medium.onnx")
            if self.automatic:
                tts.speak(text=text, play_audio=True)
            else:
                tts.speak(text=text, play_audio=False)
        except Exception as E:
            messagebox.showerror("TTS Error", f"Error sythesysing TTS: {E}")
        

    def automatic_command(self):
        if self.automatic:
            self.automatic = False
            self.transcribe_btn.config(state=tk.NORMAL)
        else:
            self.automatic = True
            self.transcribe_btn.config(state=tk.DISABLED)

        print(f"Updated Automatic to: {self.automatic}")
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio files", "*.wav *.mp3 *.ogg *.flac *.m4a"), 
                      ("All files", "*")]
        )
        if filename:
            self.file_path.set(filename)
    
    def start_transcription(self):
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select an audio file")
            return
        
        if not os.path.exists(self.file_path.get()):
            messagebox.showerror("Error", "File does not exist")
            return
        
        # Start transcription in separate thread
        self.transcribe_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_label.config(text="Transcribing...")
        
        thread = threading.Thread(target=self.transcribe_audio)
        thread.daemon = True
        thread.start()

    def start_rec(self):
        try:
            self.startrecbutton.config(state=tk.DISABLED)

            if self.recorder.startRecording():
                self.stoprecbutton.config(state=tk.NORMAL)

        except Exception as E:
            print("ERROR at start_rec: ", str(E))
            messagebox.showerror("Start Recording", str(E))

            self.startrecbutton.config(state=tk.NORMAL)
            self.stoprecbutton.config(state=tk.DISABLED)

    def stop_rec(self):
        try:
            self.stoprecbutton.config(state=tk.DISABLED)

            if self.recorder.stopRecording():
                self.startrecbutton.config(state=tk.NORMAL)

                if self.automatic:
                    print("Automation > Setting latest audio file as path...")
                    parentPath = os.path.abspath(os.path.dirname(__file__))
                    audioPath = os.path.join(parentPath, self.recorder.audiofolder)
                    filePath = os.path.join(audioPath, "latest.ogg")

                    #testpath = os.path.join(parentPath, "testAudio.ogg")

                    self.file_path.set(filePath)
                    print("Automation > Path set.")
                    print("Automation > Transcribing audio...")

                    Thread = threading.Thread(target=self.transcribe_audio)
                    Thread.daemon = True
                    Thread.start()

                    print("Automation > Thread success")
                    #self.transcribe_audio()

        except Exception as E:
            print(f"ERROR at stop_rec: {str(E)}")
            messagebox.showerror("Stop Recording", str(E))

            self.startrecbutton.config(state=tk.DISABLED)
            self.stoprecbutton.config(state=tk.NORMAL)
    
    def generate_response(self, text=None):
        try:
            transcription_text = None

            if text:
                transcription_text = text
            else:
                transcription_text = self.result_text.get("1.0", tk.END).strip()

            if not transcription_text:
                messagebox.showwarning("Warning", "No text")
                return

            self.ai_response.delete(1.0, tk.END)
            self.ai_response.insert(1.0, "Generating...")
            self.sendToAi.config(state=tk.DISABLED)

            thread = threading.Thread(target=self.get_ai_response, args=(transcription_text,))
            thread.daemon = True
            thread.start()
        except Exception as E:
            self.ai_response.delete(1.0, tk.END)
            self.ai_response.insert(1.0, f"Error! {str(E)}")

    def get_ai_response(self, transcription_text):
        try:
            if not self.ollama_client.check_ollama_running():
                if not self.ollama_client.start_ollama_service():
                    self.root.after(0, self.ai_response_error, "Failed to start Ollama service.")
                    return

            self.ollama_client.pull_model()
            response = self.ollama_client.generate_response(transcription_text)

            self.root.after(0, self.ai_response_complete, response)
        except Exception as E:
            self.root.after(0, self.ai_response_error, str(E))

    def ai_response_complete(self, response):
        self.ai_response.delete(1.0, tk.END)
        if response:
            self.ai_response.insert(1.0, response)

            if self.automatic:
                Thread = threading.Thread(target=self.doTTS)
                Thread.daemon = True
                Thread.start()
        else:
            self.ai_response.insert(1.0, "No response generated")
        self.sendToAi.config(state=tk.NORMAL)

    def ai_response_error(self, error):
        self.ai_response.delete(1.0, tk.END)
        self.ai_response.insert(1.0, f"Error: {error}")
        self.sendToAi.config(state=tk.NORMAL)
    
    def transcribe_audio(self):
        try:
            result = transcribe_audiofile(
                self.file_path.get(),
                language=self.language.get()
            )
            
            # Update UI in main thread
            self.root.after(0, self.transcription_complete, result)
            if self.automatic:
                print("Automation > Transcript complete.")
                print("Automation > Prompting A.I...")

                print(result)

                Thread = threading.Thread(target=self.generate_response, args=(result,))
                Thread.daemon = True
                Thread.start()
            
        except Exception as e:
            self.root.after(0, self.transcription_error, str(e))
    
    def transcription_complete(self, result):
        self.progress.stop()
        self.status_label.config(text="Transcription complete!")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, result)
        self.transcribe_btn.config(state=tk.NORMAL)
        self.sendToAi.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
    
    def transcription_error(self, error):
        self.progress.stop()
        self.status_label.config(text="Error occurred")
        self.transcribe_btn.config(state=tk.NORMAL)
        messagebox.showerror("Transcription Error", f"Error: {error}")
    
    def save_transcription(self):
        if not self.result_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "No transcription to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.result_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Transcription saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioTranscriberGUI(root)
    root.mainloop()

