import requests
import json
url = 'http://renat-hamatov.ru'
s = requests.Session()
send_to = f'appeals-from-tg/388856114/my'
r = s.get(f'{url}/{send_to}')
appeals = json.loads(r.text)['appeals']
appeals = appeals[::-1]
print(appeals)


def filter_set(appeals):
    def iterator_func(x):
        if "complaint" == x.get("type"):
            return True
        else:
            return False
    return filter(iterator_func, appeals)


print(list(filter_set(appeals)))