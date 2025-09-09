import re
import requests
import json
import base64

lang = 'pl'

def get_pronunciation(word):
    data = {
        'f.req': json.dumps([
            [
                [
                    'jQ1olc',
                    json.dumps([
                        word,
                        lang,
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
            filename = f"../audio/words/{word}.mp3"
            with open(filename, 'wb') as f:
                f.write(base64.b64decode(match.group(0)))
            print(f"Saved: {filename}")
        else:
            print(f"Error: No match for {word}")
    else:
        print(f"HTTP error: {response.status_code} for {word}")

with open('dictionary.txt', 'r', encoding='utf-8') as file:
    for line in file:
        polish_word = line.split(':')[0].strip()
        get_pronunciation(polish_word)
