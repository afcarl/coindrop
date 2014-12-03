import os
import sys
sys.path.append('..')
import shutil
import cPickle as cpickle
from munkgenes import *

OUTDIR = '/home/ghall/code/ga/movies'

SCRIPT = \
"""#!/usr/bin/python
import screenshot
screenshot._get_screenshot('%s', '%s')
"""

def curry(fn, *cargs, **ckwargs):
    def call_fn(*fargs, **fkwargs):
        d = ckwargs.copy()
        d.update(fkwargs)
        return fn(*(cargs + fargs), **d)
    return call_fn


def _get_screenshot(gdir, orgname):
    def screenshot(sim, path=None):
        if sim.frame_count == 5:
            if not path:
                sim.screenshot()
            else:
                sim.screenshot(path)
            sim.running = False

    fn = "%s.pickle" % orgname
    fn = os.path.join(gdir, fn)
    jpgfn = "%s.jpg" % orgname
    jpgfn = os.path.join(gdir, jpgfn)
    f = open(fn)
    org = cpickle.load(f)
    ssfunc = curry(screenshot, path=jpgfn)
    org.simulate(visualize=True, func=ssfunc)

def get_screenshot(gdir, orgname):
    jpgfn = "%s.jpg" % orgname
    jpgfn = os.path.join(gdir, jpgfn)
    if not os.path.isfile(jpgfn):
        script = SCRIPT % (gdir, orgname)
        f = open('make_ss.py', 'w')
        f.write(script)
        f.close()
        cmd = "python make_ss.py"
        os.system(cmd)
        os.unlink('make_ss.py')
    f = open(jpgfn)
    return f.read()
