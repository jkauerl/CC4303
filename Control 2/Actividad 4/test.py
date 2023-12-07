message = "testeando esto por favor funciona"

split_message = []
for i in range(0, len(message), 16):
    split_message.append(message[i:i + 16])

print(split_message)