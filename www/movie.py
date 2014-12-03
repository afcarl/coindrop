#!/usr/bin/python

import os
import sys
sys.path.append('..')
import shutil
import cPickle as cpickle

OUTDIR = '/home/ghall/code/ga/movies'

SCRIPT = \
"""#!/usr/bin/python
import movie
movie._make_movie('%s', '%s')
"""

def make_text_file():
    def jpg_sort(this, that):
        this = int(this.split('.')[0])
        that = int(that.split('.')[0])
        return cmp(this, that)

    files = os.listdir('__movie__')
    files = filter(lambda s: s.endswith('.jpg'), files)
    files.sort(jpg_sort)
    files = [os.path.join('__movie__', x) for x in files]
    files = str.join('\n', files)
    f = open('__movie__.txt', 'w')
    f.write(files)
    f.close()

def make_frames(org):
    def screenshot(sim):
        fn = '__movie__/%s.jpg' % sim.frame_count
        sim.screenshot(fn)
        if sim.frame_count >= 400:
            sim.running = False

    org.simulate(visualize=True, func=screenshot)

def _make_movie(gdir, orgname):
    fn = '%s.pickle' % orgname
    fn = os.path.join(gdir, fn)
    f = open(fn)
    org = cpickle.load(f)
    outfn = '%s.flv' % org.name
    outfn = os.path.join(OUTDIR, outfn)
    if os.path.isdir('__movie__'):
        shutil.rmtree('__movie__')
    if not os.path.isfile(outfn):
        os.mkdir("__movie__")
        make_frames(org)
        make_text_file()
        cmd = "mencoder mf://@__movie__.txt -o %s -of lavf -ovc lavc -lavcopts vcodec=flv:vbitrate=500:mbd=2:mv0:trell:v4mv:cbp:last_pred=3 -srate 22050" % outfn
        os.system(cmd)
        shutil.rmtree("__movie__")
    return outfn

def make_movie(gdir, orgname):
    script = SCRIPT % (gdir, orgname)
    f = open('make_movie.py', 'w')
    f.write(script)
    f.close()
    cmd = "python make_movie.py"
    os.system(cmd)
    os.unlink('make_movie.py')

def get_movie(gdir, orgname):
    outfn = '%s.flv' % orgname
    outfn = os.path.join(OUTDIR, outfn)
    if not os.path.isfile(outfn):
        make_movie(gdir, orgname)
