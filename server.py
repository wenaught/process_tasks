import time
from dataclasses import dataclass
from itertools import zip_longest


@dataclass
class Task:
    """A Task dataclass."""
    task_type: int
    data: str
    status: str


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
        case _:
            raise ValueError('Unknown task type')
    task.status = 'done'
