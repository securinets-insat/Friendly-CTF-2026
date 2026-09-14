import socket

host = "localhost"
port = 5018

path = b"/admin" + bytes([0xA0])   # the literal raw byte, not percent-encoded

request = (
    b"GET " + path + b" HTTP/1.1\r\n"
    b"Host: " + host.encode() + b":" + str(port).encode() + b"\r\n"
    b"Accept-Encoding: gzip, deflate\r\n"
    b"Accept: */*\r\n"
    b"User-Agent: Mozilla/5.0\r\n"
    b"Connection: close\r\n"
    b"\r\n"
)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.sendall(request)   

response = b""
while True:
    chunk = s.recv(4096)
    if not chunk:
        break
    response += chunk

print(response.decode(errors="replace"))
s.close()
