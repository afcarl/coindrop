#!/usr/bin/python

import random

class ProportionateRoullette:
    class Slot:
        def __init__(self, obj, score):
            self.obj = obj
            self.score = score
            self.probability = 0

        def __cmp__(self, other):
            return cmp(self.probability, other.probability)

        def __str__(self):
            return "%s\t%s\t%s"  % (self.obj, self.score, self.probability)

    def __init__(self):
        self.slots = []

    def build_wheel(self):
        scores = [x.score for x in self.slots]
        popsum = float(sum(scores))
        maxscore = max(scores)
        for slot in self.slots:
            slot.probability = (slot.score / popsum)
        random.shuffle(self.slots)
        #self.slots.sort(reverse=True)

    def add(self, obj, score):
        slot = self.Slot(obj, score)
        self.slots.append(slot)
    
    def remove(self, obj):
        for slot in self.slots[:]:
            if slot.obj == obj:
                self.slots.remove(slot)
                break

    def spin(self):
        self.build_wheel()
        value = random.random()
        last_cutoff = 0
        for slot in self.slots:
            if (slot.probability + last_cutoff) > value:
                break
            last_cutoff += slot.probability
        return slot.obj
