test = b"estoy probando esto"

print(test[3:5])

test2 = b"This is a message with exactly 150 bytes. It serves as an example for a text of a specific length. Python programming is versatile and widely used for various applications."

print(len(test2))

test3 = b"This is a message with exactly 150 bytes, including spaces and punctuation! It showcases the concise nature of communication within a limited character count."

print(len(test3))

test4 = b"This is a message of exactly 150 bytes. It has to be long enough to fill the required length. Let's add a bit more text to ensure it reaches the desir"

print(len(test4))


_, router_port, *routes, _ = "BGP_ROUTES\n8881\n8884 8882 8881\n8883 8882 8881\n8880 8881\nEND_ROUTES".split("\n")

print(routes)

routes = [route.split(" ") for route in routes]

print(routes)
