import inspect
import os
import sys

def update_library_path():
    sys.path.append(get_library_path())

def get_library_path():
    mod = sys.modules[__name__]
    return os.path.split(inspect.getsourcefile(mod))[0]

def curry(fn, *cargs, **ckwargs):
    def call_fn(*fargs, **fkwargs):
        d = ckwargs.copy()
        d.update(fkwargs)
        return fn(*(cargs + fargs), **d)
    return call_fn
