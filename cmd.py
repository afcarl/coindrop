#!/usr/bin/python
import os
import sys
from munkgenes import *
from optparse import OptionParser
import cPickle as cpickle
from utils import curry

def get_cli():
    parser = OptionParser()
    parser.add_option("-s", "--start", dest="start", action="store_true",
                      help="Start a simulation.")
    parser.add_option("-c", "--continue", dest="_continue", action="store_true",
                      help="Continue a simulation.")
    parser.add_option("-d", "--directory", dest="basedir",
                      help="Directory where generation data is stored.")
    parser.add_option("-w", "--watch", dest="watch",
                      help="Watch an organism.")
    parser.add_option("-t", "--timeout", dest="timeout", type="int",
                      help="Frame to stop at.")
    parser.set_defaults(_continue=False, directory='.', timeout=0)
    (options, args) = parser.parse_args()
    return (eval(str(options)), args)

def get_last_gen(opts):
    def sort_fun(x, y):
        x = int(x[4:])
        y = int(y[4:])
        return cmp(x, y)
    files = os.listdir(opts['basedir'])
    files = filter(lambda x: x.startswith('gen-'), files)
    files.sort(sort_fun)
    return int(files[-1].split('-')[-1])

def _start(opts):
    env = build_env(opts)
    run_env(env)
    
def _continue(opts):
    if opts['_continue']:
        lastgen = get_last_gen(opts)
    env = build_env(opts)
    env.load_previous(lastgen)
    run_env(env)

def build_env(opts):
    env = Environment(opts['basedir'])
    return env

def run_env(env):
    while 1:
        env.lifecycle()

def screenshot(sim):
    if sim.frame_count == 500:
        sim.screenshot("/home/ghall/www/500.png")

def short_stop(sim, timeout=0):
    if sim.frame_count == timeout:
        sim.running = False

def watch(opts):
    f = open(opts['watch'])
    org = cpickle.load(f)
    func = curry(short_stop, timeout=opts['timeout'])
    org.evaluate(visualize=True, watch=True, func=func)
    print org.results

def run():
    opts, args = get_cli()
    if opts['watch']:
        watch(opts)
    elif opts['_continue']:
        _continue(opts)
    elif opts['start']:
        _start(opts)

if __name__ == '__main__':
    run()
