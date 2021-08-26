import requests
import json

s = requests.Session()
payload = {"email": "alekssurikov2201@yandex.ru","password": "1111","chat_id": "388856114"}
print(payload)
url='http://renat-hamatov.ru'
send_to = 'telegram/connect'
print(f'{url}/{send_to}')
r = s.post(f'{url}/{send_to}', json=payload)

print (json.loads(r.text))
