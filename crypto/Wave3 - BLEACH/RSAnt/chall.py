from Crypto.Util.number import getPrime, bytes_to_long

flag = b"Securinets{k4m3h4m3h4_RSA_d3str0ys_th3_3xp0n3nt}"

# Generate a 1024-bit RSA modulus
p = getPrime(512)
q = getPrime(512)
n = p * q

e = 3

m = bytes_to_long(flag)
c = pow(m, e, n)

print("n =", n)
print("e =", e)
print("c =", c)