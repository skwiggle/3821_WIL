import asyncio

async def tcp_echo_client():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)

    message = (f'{x}\n'.encode('utf-8') for x in range(10))
    writer.writelines(f'{x}\n'.encode('utf-8') for x in range(10))
    writer.write(b'--EOF')

    data = await reader.read(10)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()

asyncio.run(tcp_echo_client())