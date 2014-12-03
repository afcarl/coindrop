import sys
sys.path.append('..')
from django.http import HttpResponse
from djangomako.shortcuts import render_to_response, render_to_string
import os
import cPickle as cpickle
import statistics
import munkgenes
import plot
from screenshot import get_screenshot
from movie import get_movie

BASEDIR = '/home/ghall/code/ga/sim'

def load_stats(basedir):
    stats = statistics.Statistics(basedir)
    stats.load_cache()
    return stats.cache

def load_org(generation, orgname):
    gdir = 'gen-%s' % generation
    fn = "%s.pickle" % orgname
    fn = os.path.join(BASEDIR, gdir, fn)
    f = open(fn)
    return cpickle.load(f)

def index(request):
    stats = load_stats(BASEDIR)
    return render_to_response('index.tmpl', {'stats':stats})

def coin_graph(request, generation, orgname):
    org = load_org(generation, orgname)
    img = plot.plot_coin_graph(org)
    return HttpResponse(img, mimetype="image/png")

def average_score_plot(request):
    stats = load_stats(BASEDIR)
    img = plot.plot_averages(stats)
    return HttpResponse(img, mimetype="image/png")

def average_mrate_plot(request):
    stats = load_stats(BASEDIR)
    img = plot.plot_mutation_rate(stats)
    return HttpResponse(img, mimetype="image/png")

def generation(request, generation=1):
    def sortfun(o1, o2):
        return cmp(o1.value, o2.value)
    gdir = 'gen-%s' % generation
    gdir = os.path.join(BASEDIR, gdir)
    files = os.listdir(gdir)
    orgs = []
    for fn in files:  
        if fn.endswith('.pickle'):
            fn = os.path.join(gdir, fn)
            f = open(fn)
            org = cpickle.load(f)
            print dir(org)
            orgs.append(org)
    orgs.sort(sortfun)
    macros = {'organisms':orgs, 'generation':generation}
    return render_to_response('generation.tmpl', macros)

def screenshot(request, generation, orgname):
    gdir = 'gen-%s' % generation
    gdir = os.path.join(BASEDIR, gdir)
    img = get_screenshot(gdir, orgname)
    return HttpResponse(img, mimetype="image/png")

def movie(request, generation, orgname):
    gdir = 'gen-%s' % generation
    gdir = os.path.join(BASEDIR, gdir)
    mpath = get_movie(gdir, orgname)
    url = 'http://www.polymerase.org/~ghall/coindrop/movies/%s.flv' % orgname
    macros = {'movie_url': url}
    return render_to_response('movie.tmpl', macros)

def organism(request, generation, orgname):
    org = load_org(generation, orgname)
    macros = {'organism': org}
    return render_to_response('organism.tmpl', macros)
