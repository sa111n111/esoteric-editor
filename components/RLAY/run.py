import sys

def read_message():
    sender = ""
    while len(sender) < 4:
        sender += sys.stdin.read(1)
    sys.stdin.read(1) # newline
    data = ""
    while True:
        ch = sys.stdin.read(1)
        if ch == "\n":
            break
        data += ch

    print(f"got {repr(data)} from {repr(sender)}", file=sys.stderr)

    return sender, data

def send_message(to, content):
    print(f"sending {repr(content)} to {repr(to)}", file=sys.stderr)
    sys.stdout.write(to + "\n")
    sys.stdout.write(content + "\n")
    sys.stdout.flush()


while True:
    sender, data = read_message()
    to = data[:4]

    msg = "Relaying: " + data[4:]


    send_message(to, msg)
