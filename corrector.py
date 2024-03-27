import os
from dotenv import load_dotenv
import requests
import subprocess
import shlex
import keyboard
import time

user_id_runner = os.getuid()
load_dotenv()

OLLAMA_API_HOST = os.getenv("OLLAMA_API_HOST", "http://127.0.0.1")
OLLAMA_API_PORT = os.getenv("OLLAMA_API_PORT", "11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")
USER_ID = os.getenv("USER_ID", "1000")
os.environ['XDG_RUNTIME_DIR'] = f'/run/user/{USER_ID}'

CTX_MAX = int(os.getenv("MAX_NEW_TOKENS", 16384))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.2))
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", 256))

def ollama_call(prompt: str) -> str:
    URI=f'{OLLAMA_API_HOST}:{OLLAMA_API_PORT}/api/generate'
    request = {
        'prompt': prompt[:CTX_MAX],
        'stream': False,
        'model': OLLAMA_MODEL,
        'system': 'You are a text corrector. You only reply with the new corrected text. Never reply with anything else.',
        'options':{
            'temperature': TEMPERATURE,
            'top_p': 0.1,
            'typical_p': 1,
            'repeat_penalty': 1.18,
            'top_k': 40,
            'frequency_penalty': 1,
            'num_ctx': CTX_MAX,
            'num_predict': MAX_NEW_TOKENS,
            'seed': -1
        }
    }

    try:
        response = requests.post(URI, json=request)
    except:
        print('Something went wrong accessing api, is Ollama running?')
        return

    if response.status_code == 200:
        return response.json()['response']
    else:
        print(f"Something went wrong accessing api. Error: {response.json()['error']}")

def create_prompt(text: str) -> str:
    return f'{text}'

def on_activate_combo():
    copied_string = subprocess.check_output(shlex.split(f"wl-paste --primary")).decode('utf-8').strip("b'\n")
    prompt = create_prompt(copied_string)
    ollama_return = ollama_call(prompt)
    if '<|im_end|>' in ollama_return:
        ollama_return = ollama_return.strip("<|im_end|>")
    
    time.sleep(0.1)
    subprocess.check_output(shlex.split(f'wl-copy "{ollama_return}"'))
    keyboard.press('ctrl')
    keyboard.press('v')
    keyboard.release('ctrl')
    keyboard.release('v')

def main():

    if user_id_runner != 0:
        print('This script must be run as root')
        return

    keyboard.add_hotkey('ctrl+alt+c', lambda: on_activate_combo())
    keyboard.wait('ctrl+alt+q')

if __name__ == "__main__":
    main()
