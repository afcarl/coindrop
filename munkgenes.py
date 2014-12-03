import random, string, math, struct
import world
import munkserver
import os
import cPickle as cpickle
import statistics
from selection import *

class Genome(list):
    def random(self, len):
        l = [random.choice([0,1]) for x in range(len)]
        super(Genome, self).__init__(l)
    
    def __iter__(self):
        return GenomeIter(self)

    def save(self, fn):
        f = open(fn, 'w')
        f.write(str.join('', map(str, self)))

    def load(self, fn):
        f = open(fn)
        g = [int(x) for x in f.read()]
        super(Genome, self).__init__(g)

class GenomeIter:
    def __init__(self, genome):
        self.genome = genome
        self.idx = 0

    def next(self):
        if self.idx >= len(self.genome):
            raise StopIteration
        bit = self.genome[self.idx]
        self.idx += 1
        return bit

    def get_byte(self):
        bits = self.genome[self.idx:self.idx+8]
        if len(bits) < 8:
            raise StopIteration
        bits = [(bit << (7 - pos)) for pos, bit in enumerate(bits)]
        self.idx += 8
        return sum(bits)

    def get_string(self, len):
        return str.join('', [chr(self.get_byte()) for x in range(len)])

    def get_8bit_unsigned(self):
        _str = self.get_string(1)
        return struct.unpack("B", _str)[0]

    def get_8bit_signed(self):
        _str = self.get_string(1)
        return struct.unpack("b", _str)[0]

    def get_16bit_unsigned(self):
        _str = self.get_string(2)
        return struct.unpack("H", _str)[0]

    def get_16bit_signed(self):
        _str = self.get_string(2)
        return struct.unpack("h", _str)[0]

    def get_32bit_unsigned(self):
        _str = self.get_string(4)
        return struct.unpack("I", _str)[0]

    def get_3216bit_signed(self):
        _str = self.get_string(4)
        return struct.unpack("i", _str)[0]

    def get_xy(self):
        x = self.get_16bit_signed() % 600
        y = self.get_16bit_signed() % 600
        return world.Vec2d(x, y)

    def get_bool(self):
        val = self.get_byte()
        return bool(val & 1)

class PhenoOp(object):
    StartCodon = 0

    def __init__(self, genome):
        self.genome = genome
        self.operate()

    def operates(cls, op):
        #return (op & 0x0F) == cls.StartCodon
        return op == cls.StartCodon
    operates = classmethod(operates)

    def operate(self, genome):
        pass

class LeverOp(PhenoOp):
    StartCodon = 12

    def operate(self):
        ctr = self.genome.get_xy()
        length = self.genome.get_16bit_unsigned()
        mass = self.genome.get_16bit_unsigned()
        inertia = self.genome.get_16bit_unsigned()
        self.args = (ctr, length, mass, inertia)

    def load(self, sim):
        lever = world.Lever(*self.args)
        sim.load(lever)

class BridgeOp(PhenoOp):
    StartCodon = 13

    def operate(self):
        ctr = self.genome.get_xy()
        length = self.genome.get_16bit_unsigned()
        rot = self.genome.get_16bit_unsigned()
        self.args = (ctr, length, rot)

    def load(self, sim):
        bridge = world.Bridge(*self.args)
        sim.load(bridge)

class PinWheel(PhenoOp):
    StartCodon = 14

    def operate(self):
        ctr = self.genome.get_xy()
        length = self.genome.get_16bit_unsigned()
        width = self.genome.get_16bit_unsigned()
        mass = self.genome.get_16bit_unsigned()
        inertia = self.genome.get_16bit_unsigned()
        self.args = (ctr,length, width, mass, inertia)

    def load(self, sim):
        bridge = world.Pinwheel(*self.args)
        sim.load(bridge)

class Organism(PhenoOp):
    Ops = [LeverOp, BridgeOp, PinWheel]

    def __init__(self, name, genome):
        self.genome = genome
        self.name = name
        self.generation = 0
        self.mutate_rate = 1000
        self.parents = []
        self.saved = False
        self.value = None
        self.results = {}

    def __cmp__(self, other):
        if hasattr(self, "value"):
            #print self.value, other.value
            return cmp(self.value, other.value)
        else:
            return cmp(id(self), id(other))

    def evaluate(self, visualize=False, watch=False, func=None):
        self.results = self.simulate(visualize=visualize, watch=watch, func=func)
        self.value = self.results['value']

    def simulate(self, func=None, visualize=False, watch=False): 
        sim = world.Simulation(visualize=visualize, watch=watch)
        self.load(sim)
        return sim.run(func)

    def save(self):
        fn = "%s-%s.txt" % (self.value, self.name)
        self.genome.save(fn)

    def screenshot(self, fn=None):
        if not fn:
            fn = "%s.jpg" % self.name
        sim = world.Simulation()
        self.load(sim)
        sim.screenshot(fn)

    def movie(self, fn=None):
        if not fn:
            fn = "%s.jpg" % self.name
        sim = world.Simulation()
        self.load(sim)
        sim.movie()

    def mutate(self):
        mutant = Genome()
        for bit in self.genome:
            if self.roll_mutate():
                bit = int(not bit)
            mutant.append(bit)
        return mutant
        #self.genome = mutant

    def crossover(self, other):
        first = random.choice([0, 1])
        second = int(not first)
        #genomes = [self.genome, other.genome]
        # get copies of the parents mutated genome
        genomes = [self.mutate(), other.mutate()]
        first_gn = genomes[first]
        second_gn = genomes[second]
        try:
            first_pt = random.randint(1, len(first_gn)) - 1
            second_pt = random.randint(1, len(second_gn)) - 1
        except:
            print len(first_gn), len(second_gn)
            raise
        top_half = first_gn[:first_pt]
        bottom_half = second_gn[second_pt:]
        gn1 = Genome(top_half + bottom_half)
        top_half = first_gn[first_pt:]
        bottom_half = second_gn[:second_pt]
        gn2 = Genome(top_half + bottom_half)
        return gn1, gn2

    def roll_mutate(self):
        mrate = 1.0 / self.mutate_rate
        return self.roll(mrate)
    
    def roll(self, chance):
        r = random.random()
        return r < chance
        
    def load(self, sim=None):
        giter = iter(self.genome)
        self.mutate_rate = giter.get_16bit_unsigned()
        while 1:
            try:
                val = giter.get_byte()
                for op in self.Ops:
                    if op.operates(val):
                        op = op(giter)
                        if sim:
                            op.load(sim)
                        break
            except StopIteration:
                break

class Environment:
    PopulationMax = 50
    PopulationMin = 10
    PopulationCull = 30
    PopulationMate = 10
    MinGenomeLength = 100
    MaxGenomeLength = 10000

    def __init__(self, basedir='.'):
        self.basedir = basedir
        self.generation = 1
        self.org_count = 0
        self.job_server = munkserver.MunkServer()
        self.reset()

    def reset(self):
        self.pool = []
        self.fill_pool()

    def make_new_organism(self):
        len = random.randint(self.MinGenomeLength, self.MaxGenomeLength)
        gn = Genome()
        gn.random(len)
        name = 'F%s_%s' % (self.generation, self.org_count)
        self.org_count += 1
        org = Organism(name, gn)
        org.generation = self.generation
        return org

    def fill_pool(self):
        for p in range(self.PopulationMax - len(self.pool)):
            self.pool.append(self.make_new_organism())
    
    def evaluate_pool(self):
        for org in self.pool:
            if org.value:
                continue
            self.job_server.submit_organism(org)
        self.job_server.run()
        self.pool.sort()

    def cull_pool(self):
        #killoff = random.randint(1, self.PopulationMax - self.PopulationMin)
        # remove still borns
        for org in self.pool[:]:
            if org.value == None:
                self.pool.remove(org)
        killoff = self.PopulationCull
        pr = self.build_roullette(inverted=False)
        for x in range(killoff):
            org = pr.spin()
            pr.remove(org)
            self.pool.remove(org)
        #self.pool = filter(lambda x: x.value != -1, self.pool)
        #self.pool = self.pool[killoff:]
        values = [x.value for x in self.pool]
        print values

    def build_roullette(self, inverted=True):
        pr = ProportionateRoullette()
        for org in self.pool:
            if inverted:
                value = 1.0 / max(1, org.value)
            else:
                value = org.value
            pr.add(org, value)
        return pr

    def mate_pool(self):
        #matecnt = random.randint(1, (self.PopulationMax - len(self.pool)) / 2)
        matecnt = self.PopulationMate
        orgs = []
        kids = []
        for mate in range(matecnt):
            pr = self.build_roullette()
            org1 = pr.spin()
            pr.remove(org1)
            org2 = pr.spin()
            gn1, gn2 = org1.crossover(org2)
            for gn in [gn1, gn2]:
                if not gn:
                    continue
                name = 'C%s_%s' % (self.generation, self.org_count)
                child = Organism(name, gn)
                child.parents = [org1.name, org2.name]
                child.generation = self.generation
                kids.append(child)
                self.org_count += 1
        self.pool = self.pool + kids

    def mutate_pool(self):
        for org in self.pool:
            org.mutate()

    def get_generation_dir(self):
        gdir = 'gen-%s' % self.generation
        return os.path.join(self.basedir, gdir)

    def save_pool(self):
        for org in self.pool:
            if not org.results or org.saved:
                continue
            org.load()
            org.saved = True
            gdir = self.get_generation_dir()
            fn = '%s.pickle' % org.name
            path = os.path.join(gdir, fn)
            f = open(path, 'w')
            cpickle.dump(org, f)

    def load_previous(self, generation):
        self.generation = int(generation)
        dirname = self.get_generation_dir()
        self.pool = []
        for fn in os.listdir(dirname):
            if fn.endswith('.pickle'):
                path = os.path.join(dirname, fn)
                if fn.startswith('report'):
                    continue
                    if fn.startswith('report'):
                        continue
                f = open(path)
                org = cpickle.load(f)
                self.pool.append(org)
        self.org_count = max([int(x.name.split('_')[-1]) for x in self.pool]) + 1
        self.generation += 1

    def lifecycle(self):
        dirname = self.get_generation_dir()
        print dirname
        os.mkdir(dirname)
        self.fill_pool()
        self.evaluate_pool()
        self.save_pool()
        self.cull_pool()
        #self.mutate_pool()
        self.generation += 1
        if self.pool:
            self.mate_pool()
        self.run_statistics()

    def run_statistics(self):
        stats = statistics.Statistics(self.basedir)
        stats.report()
