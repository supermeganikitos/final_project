import requests
import json

url = 'https://en.wikipedia.org/w/api.php.'
params = {
    'action': 'help',
    'origin': '*',
    'format': 'json',
    'generator': 'search',
    'gsrnamespace': '0',
    'gsrlimit':'5',
    'gsrsearch': 'saratov',

}
resp = requests.get(url, params)
print(resp)
with open('res.json') as f:
    json.dump(f, resp, indent=4)