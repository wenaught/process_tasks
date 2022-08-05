import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import partial
from itertools import zip_longest
import time
import uuid


pool = ThreadPoolExecutor(1)

parser = argparse.ArgumentParser(description='Start a task processing server.')
parser.add_argument('-H', '--host', type=str, default='127.0.0.1', help='server address')
parser.add_argument('-P', '--port', type=int, default=5000, help='server port')


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


async def handle(loop: asyncio.BaseEventLoop, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Callback to process a new TCP connection.

    :param loop: running event loop.
    :param reader: socket stream reader.
    :param writer: socket stream writer.
    """
    client_host, client_port = writer.get_extra_info('peername')
    print(f'Receiving from {client_host}:{client_port}.')
    while True:
        raw_data = await reader.readline()
        if not raw_data:
            break
        query_type: str
        data: str
        query_type, data = [item.strip() for item in raw_data.decode().strip().split(':', 1)]
        match query_type:
            case 'status':
                task = tasks.get(data, None)
                match task:
                    case None:
                        response = 'No such task\n'
                    case Task(_, task_data, status):
                        response = f'{data}: {status}\n' if status != 'done' else \
                            f'{data}: done, result: {task_data}\n'
            case '1' | '2' | '3':
                task = Task(int(query_type), data, 'enqueued')
                identifier = uuid.uuid4().hex[:8]
                tasks[identifier] = task
                loop.run_in_executor(pool, process, task)
                response = f'{identifier}: task scheduled\n'
            case _:
                response = f'Impossible to handle: type {query_type.strip()}, data {data}\n'
        writer.write(response.encode())
        await writer.drain()
    writer.close()
    await writer.wait_closed()
    print(f'Handled {client_host}:{client_port}.')


async def main(host: str = '127.0.0.1', port: int = 5000) -> None:
    """Entry point for the server.

    :param host: host to run on.
    :param port: port to run on.
    """
    loop = asyncio.get_running_loop()
    server = await asyncio.start_server(partial(handle, loop), host, port)
    print(f'Serving on {server.sockets[0].getsockname()}. Hit CTRL-C to stop.')
    await server.serve_forever()


if __name__ == '__main__':
    try:
        args = parser.parse_args()
        asyncio.run(main(host=args.host, port=args.port))
    except KeyboardInterrupt:
        print('\nServer shut down.')
