import os
import re
import requests
import json
import base64

class MediaController:
    lang = 'en'

    def __init__(self, lang='en', path='assets/data/EN/audio/'):
        self.lang = lang.lower()
        self.path = path

    def get(self, word):
        filename = f"{self.path}/{word}.mp3"
        if not os.path.exists(filename):
            self.save_sound(word)
        return filename if os.path.exists(filename) else None

    def save_sound(self, word):
        data = {
            'f.req': json.dumps([
                [
                    [
                        'jQ1olc',
                        json.dumps([
                            word,
                            self.lang,
                            None,
                            json.dumps(None),
                        ]),
                        None,
                        'generic',
                    ]
                ]
            ]),
        }

        response = requests.post('https://translate.google.com/_/TranslateWebserverUi/data/batchexecute', data=data)
        
        if response.status_code == 200:
            match = re.search(r'//OE[^\\]+', response.text)
            if match:
                filename = f"{self.path}/{word}.mp3"
                with open(filename, 'wb') as f:
                    f.write(base64.b64decode(match.group(0)))
            else:
                print(f"Error: No match for '{word}'")
        else:
            print(f"HTTP error: {response.status_code} for '{word}'")
