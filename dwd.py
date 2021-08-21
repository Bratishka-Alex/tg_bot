import requests
import json

s = requests.Session()
payload = {"email": "tes185548t@mail.ru", "password": "11111", "firstname": "test", "secondname": "test", "house": "test", "flat": "1"}
url='http://renat-hamatov.ru'
send_to = 'signup'
print(f'{url}/{send_to}')
r = s.post(f'{url}/{send_to}', json=payload)

print (json.loads(r.text))
