import asyncio
import re

async def handle_echo(reader, writer):
    data = await reader.readuntil(b'--EOF')
    message = data.decode('utf-8')
    info = re.split('\n', message)
    addr = writer.get_extra_info('peername')

    print(f"Received:\n {info} from {addr}")

    print(f"Send: I received it")
    writer.write(b'Sent')
    await writer.drain()

    print("Close the connection")
    writer.close()

async def main():
    server = await asyncio.start_server(
        handle_echo, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())

