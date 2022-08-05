import asyncio
from asyncio.trsock import TransportSocket
from dataclasses import dataclass
from itertools import zip_longest
import time
from typing import cast
import sys


@dataclass
class Task:
    """A Task dataclass."""
    task_type: int
    data: str
    status: str


tasks: dict[str, Task] = {}


def process(task: Task) -> None:
    """Process a Task bases on its type.

    :param task: the Task to process.
    """
    task.status = 'processing'
    match task.task_type:
        case 1:
            time.sleep(2)
            task.data = ''.join(reversed(task.data))
        case 2:
            time.sleep(5)
            task.data = ''.join(second + first for first, second in
                                zip_longest(task.data[::2], task.data[1::2], fillvalue=''))
        case 3:
            time.sleep(7)
            task.data = ''.join(char * pos for pos, char in enumerate(task.data, start=1))
    task.status = 'done'


async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    client_host, client_port = writer.get_extra_info('peername')
    print(f'Connected from {client_host}:{client_port}')
    while True:
        raw_data = await reader.readline()
        if not raw_data:
            break
        query_type, data = raw_data.decode().strip().split(':', 1)
        writer.write(f'Query type was {query_type.strip()} and data sent was {data.strip()}.\n'.encode())
        await writer.drain()
    writer.close()
    await writer.wait_closed()
    print(f'Handled {client_host}:{client_port}.')


async def main(host: str = '127.0.0.1', port: str = '5000') -> None:
    server = await asyncio.start_server(handle, host, int(port))
    socket_list = cast(tuple[TransportSocket, ...], server.sockets)
    addr = socket_list[0].getsockname()
    print(f'Serving on {addr}. Hit CTRL-C to stop.')
    await server.serve_forever()


if __name__ == '__main__':
    try:
        asyncio.run(main(*sys.argv[1:]))
    except KeyboardInterrupt:
        print('\nServer shut down.')
