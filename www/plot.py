import matplotlib
matplotlib.use('Agg')
import matplotlib.image as image
import matplotlib.pyplot as plt
import StringIO

def stdout_fig(fig):
    output = StringIO.StringIO()
    fig.savefig(output, format="png")
    output.seek(0)
    return output.read()

def plot_averages(cache):
    y = [gen.get('avgscore', None) for gen in cache]
    y = filter(lambda val: val != None, y)
    y = filter(lambda val: val < 10 ** 6, y)
    x = range(1, len(y) + 1)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y, '-o', alpha=0.7, mfc='orange')
    plt.title("Average Score")
    plt.xlabel("Generations")
    plt.ylabel("Average Score")
    ax.grid()
    return stdout_fig(fig)

def plot_mutation_rate(cache):
    data = [gen.get('avgmrate', None) for gen in cache]
    data = filter(lambda x: x != None, data)
    data = [0] + data
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(data, '-o', alpha=0.7, mfc='orange')
    plt.title("Average Mutation Rate")
    plt.xlabel("Generations")
    plt.ylabel("Average Mutation Rate")
    ax.grid()
    return stdout_fig(fig)

def plot_coin_graph(org):
    fig = plt.figure()
    cg = org.results.get('coin_graph', {})
    ax = fig.add_subplot(111)
    for coin in cg:
        y = range(len(cg[coin]))
        x = cg[coin]
        ax.plot(x, y, label=coin)
    leg = ax.legend(cg.keys(), 'upper center')
    plt.title("Coin Graph")
    plt.xlabel("Time")
    plt.ylabel("Coin Collection")
    ax.grid()
    return stdout_fig(fig)
