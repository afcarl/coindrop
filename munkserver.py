#!/usr/bin/python

import math, sys, time
import os
import threading
import tempfile
import Queue

import munkgenes
import utils

Script = """
#!/usr/bin/python
import sys
sys.path.append("%s")
import munkgenes
genome = munkgenes.Genome(%s)
org = munkgenes.Organism("eval", genome)
try:
    org.evaluate()
    results = org.results
except:
    results = None

f = open("%s", 'w')
f.write(str(results))
f.close()
"""

class MunkServer:
    def __init__(self, num_worker_threads=4):
        self.num_worker_threads = num_worker_threads
        self.jobs = Queue.Queue()
        self.start_threads()

    def submit_organism(self, organism):
        self.jobs.put(organism)

    def worker_func(self):
        while True:
            org = self.jobs.get()
            self.evaluate_organism(org)
            self.jobs.task_done()
        
    def start_threads(self):
        for i in range(self.num_worker_threads):
            t = threading.Thread(target=self.worker_func)
            t.setDaemon(True)
            t.start()

    def run(self):
        self.jobs.join()

    def evaluate_organism(self, organism):
        fd, fn = tempfile.mkstemp()
        outfn = "%s.out" % fn
        txt = Script % (utils.get_library_path(), organism.genome, outfn)
        os.close(fd)
        f = open(fn, 'w')
        f.write(txt)
        f.close()
        cmd = "/usr/bin/python %s" % fn
        os.system(cmd)
        f = open(outfn, 'r')
        results = f.read()
        results.strip()
        results = eval(results)
        if results != None:
            organism.results = results
            organism.value = results['value']
        os.unlink(fn)
        os.unlink(outfn)

if __name__ == '__main__':
    import time
    ms = MunkServer()
    orgs = []
    for x in range(5):
        g = munkgenes.Genome()
        g.random(10000)
        org = munkgenes.Organism(str(x), g)
        orgs.append(org)
        ms.submit_organism(org)
    before = time.time()
    ms.run()
    for org in orgs:
        print org.results
    after = time.time()
    print after - before

    before = time.time()
    for org in orgs:
        try:
            org.evaluate()
        except:
            continue
    after = time.time()
    print after - before
