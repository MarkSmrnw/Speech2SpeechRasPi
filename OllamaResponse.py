import os
import sys
import time
import json
import requests
import subprocess

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", temperature=0.8):
        self.base_url = base_url
        self.model_name = "qwen3:4b"
        self.temperature = temperature
        self.ollama_process = None
        self.history_path = "History/latest.json"

    def check_ollama_running(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def stop_ollama_service(self):
        if self.ollama_process:
            try:
                self.ollama_process.terminate()
                self.ollama_process.wait(timeout=5)
                print("Ollama service stopped.")
            except:
                self.ollama_process.kill()
        
    def start_ollama_service(self):
        try:
            self.ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
            )

            time.sleep(3) #Warten damit OLLAMA startet

            if self.check_ollama_running():
                print("Ollama running.")
                return True
            else:
                print("Failed to start Ollama.")
                return False
            
        except FileNotFoundError:
            print("Ollama not found. Please install Ollama.")
            return False
        except Exception as E:
            print("Error starting Ollama: ", str(E))
            return False
        
    def pull_model(self):
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name":self.model_name},
                stream=True,
                timeout=300
            )

            if response.status_code == 200:
                print("Pulling model...")

                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if "status" in data:
                            print(f"Status: {data['status']}")
                        if data.get("status") == "success":
                            print("Model pulles successfully")
                            return True
                return False
        except Exception as E:
            print("Error pulling model: ", str(E))
            return False

    def clean_response(self, response):
        import re
        cleaned = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
        return cleaned.strip()

    def set_temperature(self, temperature):
        """Set the temperature for AI responses (0.0 to 1.0)"""
        self.temperature = max(0.0, min(1.0, temperature))
        print(f"Temperature set to: {self.temperature}")

    def generate_response(self, prompt, stream=False):
        try:
            payload = {
                "model":self.model_name,
                "prompt": prompt + " /no_think",
                "stream": stream,
                "temperature": self.temperature,
                "system": 
"""
Your name is Thorsten.
You are a helpful a.i chatbot. Be friendly but not too formal. 
Speak like the user is your friend. 
Respond in the users language unless the user says otherwise. 

- DO NOT use emojis (THIS IS VERY IMPORTANT).
- DO NOT use text formatting
""",
            }

            print(f"Sending payload: {json.dumps(payload, indent=2)}")

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=stream,
                timeout=60
            )

            print(f"Response status: ", response.status_code)

            if response.status_code == 200:
                if stream:
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            if "response" in data:
                                chunk = data["response"]

                                print(chunk, end="", flush=True)
                                full_response += chunk
                            if data.get("done", False):
                                print()
                                break

                    return self.clean_response(full_response)
                else:
                    data = response.json()
                    raw_response = data.get("response", "")
                    return self.clean_response(raw_response)
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                

        except Exception as E:
            print("Error generating response: ", str(E))
            return None
        
    def create_history(self):
        newData = {"time":time.time(), "msgs":{}}
        try:
            os.makedirs(self.history_path, exist_ok=True)
            print("new folder OK!")
        except:
            print("makedirs fail. This means that the Folder probably exists.")
            pass
        try:
            with open(self.history_path, "r+") as file:
                file.truncate(0)
                json.dump(newData, file, indent=3)
                print("File create OK!")
                file.close()
        except Exception as E:
            print(f"Creation failed. {E}")
        
    def get_history(self):
        try:
            with open(self.history_path, "r+") as file:
                data = json.load(file)
                timestamp = time.time()

                if "msgs" in data and "time" in data:
                    print("Has blocks")
                    
                    if time.time()-float(data["time"]) > 300:
                        print("HISTORY OLD!")
                        self.create_history()
                        return {}
                    else:
                        # HISTORY TIME GOOD. USING
                        print("History OK.")
                        data["time"] = timestamp
                        json.dump(data, file, indent=3)
                        return data["msgs"]

                file.close()
        except Exception as E:
            print("Error at get history:")
            print(str(E))
    
def main():
    client = OllamaClient()

    if not client.check_ollama_running():
        print("Ollama is not running. Attempting to start...")
        if not client.start_ollama_service():
            print("Failed to start Ollama service.")
            return
    
    print("Ollama running.")
    print("Checking if model is avalible...")

    if not client.pull_model():
        print("Failed to pull model.")
        return
    
    print("Model avalible.")
    print("Running test prompt for debugging...")

    test = client.generate_response("Hallo. Funkt du?")
    print(f"Response: {test}")

if __name__ == "__main__":
    OC = OllamaClient()
    OC.create_history()
    h =OC.get_history()
    print(h)