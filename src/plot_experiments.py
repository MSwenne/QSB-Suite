from io import TextIOWrapper
from matplotlib import pyplot as plt
import json

log = False
only_palindrome = False
only_vector = False

def plot_data(data, type, color, log):
    y = []
    for out in data:
        if out.startswith("nodecount"):
            y.append(int(out.split(":")[1]))
    plt.plot(y, label=type, color=color)
    plt.xlabel("#gates aplied")
    plt.ylabel("#nodes")
    if log:
        plt.yscale("symlog")
    return min(y), max(y)

def plot_data_matmat(data, type, prefix, color):
    y = []
    x = []
    for out in data:
        if out.startswith("nodecount "+type):
            temp = out.split(":")[1].split("at")
            if type == "mat":
                y.append(int(temp[0]))
            else:
                y.append(int(temp[0]))
            x.append(int(temp[1]))
    if not only_palindrome:
        if type == "mat" and not only_vector:
            plt.plot(x, y, color=color,linestyle="--")
        if type == "vec":
            plt.plot(x, y, label=prefix+" "+type, color=color)
        plt.xticks([x[0], x[-1]])
    plt.xlabel("#gates aplied")
    plt.ylabel("#nodes")
    return (min(y),max(y))


def plot_matmat(data, type, color):
    min1, max1 = plot_data_matmat(data, "mat", type, color)
    min2, max2 = plot_data_matmat(data, "vec", type, color)
    p_start = []
    p_end = []
    for out in data:
        if out.startswith("palindrome start"):
            p_start.append(int(out.split(":")[1]))
        if out.startswith("palindrome end"):
            p_end.append(int(out.split(":")[1]))
    mn = min(min1,min2)
    mx = max(max1,max2)
    if only_vector:
        mn = min2
        mx = max2
    return p_start, p_end, mn, mx 

def process_nodecount(filename: str, f: TextIOWrapper):
    for line in f.readlines():
        data = [x for x in json.loads(line)]
        if data[0] == "matvec":
            min1, max1 = plot_data(data, "matvec", "r", log)
        if data[0] == "greedy":
            min2, max2 = plot_data(data, "greedy", "b", log)
        if data[0] == "matmat":
            p_start, p_end, min3, max3 = plot_matmat(data, "matmat", "g")
        if data[0] == "balance":
            _, _, min4, max4 = plot_matmat(data, "balance", "k")
    for x in p_start:
        plt.vlines(x, min([min1, min2, min3, min4]), max([max1, max2, max3, max4]), colors="gray",alpha=0.2,linestyles="--")
    for x in p_end:
        plt.vlines(x, min([min1, min2, min3, min4]), max([max1, max2, max3, max4]), colors="gray",alpha=0.2,linestyles="--")
    plt.legend(prop={'size':9})
    plt.savefig('plot/'+filename+".png", dpi=200)

def process_time(filename: str, f: TextIOWrapper):
    plt.subplot(111)
    y = []
    labels = []
    for line in f.readlines():
        data = [x for x in json.loads(line)]
        if data[0][-5:] == "_time":
            y.append([])
            for out in data:
                if out.startswith("seconds"):
                    y[-1].append(float(out.split(":")[1]))
            labels.append(data[0][:-5])
    plt.boxplot(y, labels=labels)
    plt.ylabel("time in seconds")
    if log:
        plt.yscale("symlog")
    plt.savefig('plot/'+filename+"__time.png", dpi=200)

if __name__ == '__main__':
    filenames = ["grover_8q"]
    only_palindrome = False
    for filename in filenames:
        log = True
        with open("data/"+filename+".txt", "r") as f:
            only_vector = False
            process_nodecount(filename+"_mat", f)
            plt.clf()
        with open("data/"+filename+".txt", "r") as f:
            only_vector = True
            process_nodecount(filename+"_vec", f)
            plt.clf()
        log = False
        with open("data/"+filename+".txt", "r") as f:
            process_time(filename, f)
            plt.clf()
