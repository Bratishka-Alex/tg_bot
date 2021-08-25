d = {}
d['lol'] = 'lel'
d.setdefault('lel', []).append(2)
d.setdefault(1, []).append(3)
d.setdefault(5, []).append(6)
k = dict()
k['dla'] = d
print(k)