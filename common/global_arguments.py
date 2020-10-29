import argparse

_arguments = None


def init_empty_arguments():
    args = argparse.Namespace()
    set_global_args(args)
    return args


def set_global_args(args):
    global _arguments
    _arguments = args


def get_global_args():
    return _arguments


def get_argument(name: str):
    arg = getattr(_arguments, name)
    if arg is None:
        raise RuntimeError("Argument %s doesn't exists." % name)
    return arg


def set_argument(name: str, value):
    global _arguments
    setattr(_arguments, name, value)
