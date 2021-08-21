import requests
import json

s = requests.Session()
payload = {"email": "test@mail.ru","password": "11111","chat_id": "3"}
print(payload)
url='http://renat-hamatov.ru'
send_to = 'conect-tg'
print(f'{url}/{send_to}')
r = s.post(f'{url}/{send_to}', json=payload)

print (json.loads(r.text))
