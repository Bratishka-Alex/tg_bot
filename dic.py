import requests
import json

s = requests.Session()
payload = {"email": "test3@mail.ru","password": "111","chat_id": "388856114"}
print(payload)
url='http://renat-hamatov.ru'
send_to = 'telegram/connect'
print(f'{url}/{send_to}')
r = s.post(f'{url}/{send_to}', json=payload)

print (json.loads(r.text))
