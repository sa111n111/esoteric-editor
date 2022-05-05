import sys
import os
import signal
import asyncio
import asyncio_channel as ch
import traceback

component_channels = {}

RESET = "\033[0m"
LOG_COLOR = "\033[38;5;69m"
MSG_COLOR = "\033[38;5;195m"
TITLE = "\033[1m"

async def process_stdout(proc, name):
    while True:
        receiver = ""
        while receiver == "":
            receiver = await proc.stdout.readexactly(5)
        receiver = receiver[:-1]
        data = (await proc.stdout.readuntil(b"\n"))[:-1]

        print(f"{MSG_COLOR}{name.decode('utf-8')}->{receiver.decode('utf-8')}{RESET} {repr(data)}")
        await component_channels[receiver].put((name, data))

async def send_stdin(proc, ch):
    async for (sender, data) in ch:
        proc.stdin.write(sender + b"\n" + data + b"\n")
        await proc.stdin.drain()

async def pretty_stderr(proc, name):
    while True:
        line = await proc.stderr.readline()
        print(f"{LOG_COLOR}LOG [{name}]{RESET} {line.decode('utf-8').strip()}")

async def start_component(cmd, name):
    print(f"{TITLE}Starting {name}{RESET}")
    name_b = name.encode("utf-8")

    msg_channel = ch.create_channel()
    component_channels[name_b] = msg_channel

    proc = await asyncio.create_subprocess_shell(
        cmd,
        cwd=os.path.join("components", name), # Undocumented!
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    await asyncio.gather(
        process_stdout(proc, name_b),
        send_stdin(proc, msg_channel),
        pretty_stderr(proc, name),
    )

async def main():
    os.setpgrp() # create new process group, become its leader

    try:
        await asyncio.gather(
            start_component("python3 run.py /dev/ttys005", "INTR"),
            start_component("python3 run.py", "RLAY"),
            start_component("python3 run.py", "CONS"),
        )
    except:
        traceback.print_exc()
    finally:
        print("bye")
        os.killpg(0, signal.SIGKILL) # kill all processes in my group

if __name__ == "__main__":
    asyncio.run(main())
