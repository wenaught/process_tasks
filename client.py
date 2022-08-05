import argparse
import functools
import socket
import time
from typing import TextIO

parser = argparse.ArgumentParser(description='Send a task for processing or get its status.')
parser.add_argument('-H', '--host', type=str, default='127.0.0.1', help='server address')
parser.add_argument('-P', '--port', type=int, default=5000, help='server port')

subs = parser.add_subparsers(help='task operations')

task_p = subs.add_parser('task', help='send a new task to server')
task_p.add_argument('task_type', type=str, help='type of the task', choices=['1', '2', '3'])
task_p.add_argument('task_data', metavar='task data', type=str, help='content of the message')
task_p.add_argument('--packet', action='store_true', help='run in packet mode')

status_p = subs.add_parser('status', help='get task status')
status_p.add_argument('id', type=str, help='identifier of the task')


def send_and_receive(writer: TextIO, reader: TextIO, message: str):
    """Utility function to package send and receive actions on the socket.

    :param writer: file-like input interface.
    :param reader: file-like output interface.
    :param message: message to write.
    :return: stripped response string.
    """
    writer.write(message)
    writer.flush()
    response = reader.readline()
    return response.strip()


def client(args: argparse.Namespace) -> None:
    """Entry point for client.

    :param args: an object containing parsed arguments.
    """
    conn = socket.create_connection((args.host, args.port))
    reader = conn.makefile('r')
    writer = conn.makefile('w')
    bound_send_and_receive = functools.partial(send_and_receive, writer, reader)
    packet = False
    match args:
        case argparse.Namespace(id=identifier):
            message = f'status: {identifier}\n'
        case argparse.Namespace(task_type=task_type, task_data=task_data, packet=packet):
            message = f'{task_type}: {task_data}\n'
        case _:
            raise ValueError(f'Unexpected input was received: {args}')
    response: str = bound_send_and_receive(message)
    print(response)
    identifier = response.split(':', 1)[0]
    if packet:
        print('Waiting for updates.')
        done = False
        message = f'status: {identifier}\n'
        while not done:
            response = bound_send_and_receive(message)
            print(response)
            time.sleep(2)
            done = 'done' in response
    conn.close()


if __name__ == "__main__":
    client(parser.parse_args())
