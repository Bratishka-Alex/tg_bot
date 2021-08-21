import requests
import json

s = requests.Session()
payload = {"chat_id": "3"}
url='http://renat-hamatov.ru'
send_to = 'disconect-tg'
print(f'{url}/{send_to}')
r = s.post(f'{url}/{send_to}', json=payload)

print (json.loads(r.text))
