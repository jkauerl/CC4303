test = b"1 2 3 \r\n\r\n a"

print(test)
print(test.decode())
print(test.decode().split("\r\n"))

