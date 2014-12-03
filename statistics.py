import os
import sys
import cPickle as cpickle
from munkgenes import *
from utils import curry


class CacheGeneration(dict):
    def load(self, path):
        orgs = self.load_organisms(path)
        if not len(orgs):
            return False
        #self.write_screenshots(orgs)
        self.calculate_score_average(orgs)
        self.calculate_score_mrate(orgs)
        self.compute_macros(orgs)
        return True

    def load_organisms(self, path):
        self['generation'] = int(path.split('-')[-1])
        files = os.listdir(path)
        orgs = []
        for fn in files:
            if fn.endswith('.pickle'):
                fn = os.path.join(path, fn)
                f = open(fn)
                try:
                    org = cpickle.load(f)
                    orgs.append(org)
                except:
                    continue
        return orgs

    def calculate_score_average(self, orgs):
        values = [org.value for org in orgs]
        avg = sum(values) / float(len(values))
        self['avgscore'] = avg

    def calculate_score_mrate(self, orgs):
        values = [org.mutate_rate for org in orgs]
        avg = sum(values) / float(len(values))
        avg = 1.0 / avg
        self['avgmrate'] = avg

    def compute_macros(self, orgs):
        self['values'] = [org.value for org in orgs]
        gnum = self['generation']
        values = self['values']
        self['avgscore'] = sum(values) / float(len(values))
        self['maxscore'] = max(values)
        kids = filter(lambda x: x.generation == gnum and x.parents, orgs)
        self['kids'] = len(kids)
        noobs = filter(lambda x: x.generation == gnum and not x.parents, orgs)
        self['noobs'] = len(noobs)
        lastgen = filter(lambda x: x.generation != gnum, orgs)
        self['lastgen'] = len(lastgen)

    def write_screenshots(self, orgs):
        def screenshot(sim, path=None):
            if sim.frame_count == 500:
                if not path:
                    sim.screenshot()
                else:
                    sim.screenshot(path)
                sim.running = False

        for org in orgs:
            fn = "gen-%s/%s.jpg" % (self['generation'], org.name)
            if os.path.isfile(fn):
                continue
            ssfunc = curry(screenshot, path=fn)
            try:
                org.simulate(visualize=False, func=ssfunc)
            except:
                continue

class Statistics:
    def __init__(self, basedir='.'):
        self.basedir = basedir

    def report(self):
        self.load_cache()
        self.scan()
        self.save_cache()

    def scan(self):
        if len(self.cache):
            last_gen = self.cache[-1]['generation']
        else:
            last_gen = 0
        files = os.listdir(self.basedir)
        for fn in files:
            if fn.startswith('gen-'):
                this_gen = int(fn.split('-')[-1])
                if this_gen > last_gen:
                    self.load_generation(fn)

    def load_cache(self):
        fn = os.path.join(self.basedir, 'statistics.pickle')
        if os.path.isfile(fn):
            f = open(fn)
            self.cache = cpickle.load(f)
        else:
            self.cache = []
        self.sort_cache()

    def sort_cache(self):
        def sort_fun(x, y):
            return cmp(x['generation'], y['generation'])
        self.cache.sort(sort_fun)
    
    def save_cache(self):
        self.sort_cache()
        fn = os.path.join(self.basedir, 'statistics.pickle')
        f = open(fn, 'w')
        cpickle.dump(self.cache, f)
        f.close()

    def load_generation(self, gdir):
        print "Loading %s" % gdir
        cg = CacheGeneration()
        path = os.path.join(self.basedir, gdir)
        cg.load(path)
        self.cache.append(dict(cg))

if __name__ == "__main__":
    stats = Statistics(sys.argv[1])
    stats.report()
