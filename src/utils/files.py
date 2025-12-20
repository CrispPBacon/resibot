import os
import inspect

root_dir = os.path.dirname(os.path.abspath(os.path.join(__file__, "..", "..")))


def get_file_dir():
    caller_file = inspect.stack()[1].filename
    return os.path.dirname(os.path.abspath(caller_file))
