import asyncio
import sys


async def tcp_client(host: str = '127.0.0.1', port: str = '5000'):
    reader, writer = await asyncio.open_connection(host, int(port))
    writer.write('1: asdf\n'.encode())
    await writer.drain()
    data = await reader.readline()
    print(f'Received: {data.decode()}')
    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(tcp_client(*sys.argv[1:]))
