from io import TextIOWrapper
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import json
import os

def plot_avg_nodecount(filename, type, color, i):
    y_avg_mat = []
    y_std_mat = []
    y_avg_vec = []
    y_std_vec = []
    prev = -1
    with open("data/"+filename+".txt", "r") as f:
        prev_loc_mat = 0
        prev_loc_vec = 0
        for line in f.readlines():
            data = [x for x in json.loads(line)]
            index = int(data[0].split("_")[1])
            if index != prev:
                y_mat = []
                y_vec = []
            for out in data:
                if out.startswith("nodecount"):
                    if type == "balanced" or type == "relationBased":
                        val, loc = out.split(":")[1].split("at")
                        if out.startswith("nodecount mat"):
                            for _ in range(prev_loc_mat,int(loc)):
                                y_mat.append(int(val))
                            prev_loc_mat = int(loc)
                        if out.startswith("nodecount vec"):
                            for _ in range(prev_loc_vec,int(loc)):
                                y_vec.append(int(val))
                            prev_loc_vec = int(loc)
                    else:
                        y_vec.append(int(out.split(":")[1]))
            if index != prev:
                y_std_vec.append(np.std(y_vec))
                y_avg_vec.append(np.mean(y_vec))
                if type == "balanced" or type == "relationBased":
                    y_std_mat.append(np.std(y_mat))
                    y_avg_mat.append(np.mean(y_mat))
                prev = index


        y_avg_vec = np.array(y_avg_vec)
        y_std_vec = np.array(y_std_vec)
        y_avg_mat = np.array(y_avg_mat)
        y_std_mat = np.array(y_std_mat)
        # plt.plot(range(i,i+len(y_avg_vec)), y_avg_vec+y_std_vec, color = color, alpha=0.3)
        plt.plot(range(i,i+len(y_avg_vec)), y_avg_vec, label=type, color = color)
        # plt.plot(range(i,i+len(y_avg_vec)), y_avg_vec-y_std_vec, color = color, alpha=0.3)
        # plt.fill_between(range(i,i+len(y_avg_vec)), y_avg_vec, y_avg_vec+y_std_vec, color = color, alpha=0.1)
        if type == "balanced" or type == "relationBased":
            # plt.plot(range(i,i+len(y_avg_mat)), y_avg_mat+y_std_mat, color = color, alpha=0.15, linestyle="--")
            plt.plot(range(i,i+len(y_avg_mat)), y_avg_mat, label=type+" gate", color = color, alpha=0.5, linestyle="--")
            # plt.plot(range(i,i+len(y_avg_mat)), y_avg_mat-y_std_mat, color = color, alpha=0.15, linestyle="--")
            # plt.fill_between(range(i,i+len(y_avg_mat)), y_avg_mat, y_avg_mat+y_std_mat, color = color, alpha=0.05, linestyle="--")
        plt.xticks(range(i,i+len(y_avg_vec)))

def plot_nodecount_timeline(filename, type, color, i):
    with open("data/"+filename+"_mean.txt", "r") as f:
        for line in f.readlines():
            data = [x for x in json.loads(line)]
            y_vec = []
            y_mat = []
            if int(data[0].split("_")[1].split("_")[0]) == i:
                for out in data[1:]:
                    if data[0].endswith("mat"):
                        y_mat.append(out)
                    else:
                        y_vec.append(out)
                if data[0].endswith("mat"):
                    plt.plot(range(len(y_mat)), y_mat, color = color, linestyle="--")
                else:
                    plt.plot(range(len(y_vec)), y_vec, label=data[0], color = color)

def store_avg_of_runs(filename):
    prev = -1
    y_mat = []
    y_vec = []
    i = 0
    prev_loc_mat = 0
    prev_loc_vec = 0
    with open("data/"+filename+".txt", "r") as f:
        for line in f.readlines():
            prev_loc_mat = 0
            prev_loc_vec = 0
            data = [x for x in json.loads(line)]
            index = int(data[0].split("_")[1])
            if index != prev:
                if i != 0:
                    df_vec = pd.DataFrame(y_vec)
                    mean_vec = list(df_vec.mean(axis=0))
                    mean_vec.insert(0, prev_name)
                    with open("data/"+filename+"_mean.txt", "a") as f:
                        f.write(json.dumps(mean_vec))
                        f.write("\n")
                    if type == "balanced" or type == "relationBased":
                        df_mat = pd.DataFrame(y_mat)
                        mean_mat = list(df_mat.mean(axis=0))
                        mean_mat.insert(0, prev_name+"_mat")
                        with open("data/"+filename+"_mean.txt", "a") as f:
                            f.write(json.dumps(mean_mat))
                            f.write("\n")
                prev_name = data[0]
                i += 1
                y_mat = []
                y_vec = []
            y_mat.append([])
            y_vec.append([])
            for out in data:
                if out.startswith("nodecount"):
                    if type == "balanced" or type == "relationBased":
                        val, loc = out.split(":")[1].split("at")
                        if out.startswith("nodecount mat"):
                            print(prev_loc_mat,loc)
                            for _ in range(prev_loc_mat,int(loc)):
                                y_mat[-1].append(int(val))
                            prev_loc_mat = int(loc)
                        if out.startswith("nodecount vec"):
                            for _ in range(prev_loc_vec,int(loc)):
                                y_vec[-1].append(int(val))
                            prev_loc_vec = int(loc)
                    else:
                        y_vec[-1].append(int(out.split(":")[1]))
            prev = index
    df_vec = pd.DataFrame(y_vec)
    mean_vec = list(df_vec.mean(axis=0))
    mean_vec.insert(0, prev_name)
    with open("data/"+filename+"_mean.txt", "a") as f:
        f.write(json.dumps(mean_vec))
        f.write("\n")
    if type == "balanced" or type == "relationBased":
        df_mat = pd.DataFrame(y_mat)
        mean_mat = list(df_mat.mean(axis=0))
        mean_mat.insert(0, prev_name+"_mat")
        with open("data/"+filename+"_mean.txt", "a") as f:
            f.write(json.dumps(mean_mat))
            f.write("\n")

def plot_time(filename, types, colors, k):
    fig1 = plt.figure()
    plt.xlabel("depth")
    plt.ylabel("time in seconds")
    plt.title("Grover's search algorithm")
    fig2 = plt.figure()
    ax1 = fig1.add_subplot(111)
    ax2 = fig2.add_subplot(111)
    prev = -1
    for j, type in enumerate(types):
        i = k
        y = []
        ys = []
        labels = []
        with open("data/"+filename+"/"+filename+"_"+type+"_time.txt", "r") as f:
            for line in f.readlines():
                data = [x for x in json.loads(line)]
                index = int(data[0].split("_")[1])
                if index != prev:
                    ys = []
                    y.append(ys)
                    y
                    labels.append(i)
                    i+=1
                prev = index
                for out in data:
                    if out.startswith("seconds"):
                        ys.append(float(out.split(":")[1]))
            ax1.errorbar(labels, np.mean(y, axis=1), np.std(y,axis=1),label=type, color=colors[j], capsize=2)
            # ax2.errorbar(labels, np.mean(y, axis=1), np.std(y,axis=1), color=colors[j], capsize=2)
            # plt.xlabel("#qubits")
            # plt.ylabel("time in seconds")
            # plt.title("Grover's search algorithm using "+ type + " method")
            # fig2.savefig('plot/'+filename+"/"+filename+"_"+type+"_time.png", dpi=200)
            # fig2.clf()
            # ax2 = fig2.add_subplot(111)
    ax1.legend()
    fig1.savefig('plot/'+filename+"/"+filename+"_time.png", dpi=200)
            # plt.clf()

if __name__ == '__main__':
    filenames = ["supremacy"]
    types = ["successorState", "relationBased", "greedy", "balanced"]
    colors = ["r", "b", "g", "y"]
    start_value = 5
    over_time_value = 11
    for filename in filenames:
        for i, type in enumerate(types):
            if os.path.exists("data/"+filename+"/"+filename+"_"+type+"_mean.txt"):
                os.remove("data/"+filename+"/"+filename+"_"+type+"_mean.txt")
            store_avg_of_runs(filename+"/"+filename+"_"+type)
        for i, type in enumerate(types):
            plot_avg_nodecount(filename+"/"+filename+"_"+type, type, colors[i],start_value)
            plt.xlabel("depth")
            plt.ylabel("#nodes")
            plt.legend(prop={'size':9})
            plt.yscale("log")
            plt.title("Grover's search algorithm")
        plt.savefig('plot/'+filename+"/"+filename+".png", dpi=200)
        plt.clf()
        for i, type in enumerate(types):
            plot_nodecount_timeline(filename+"/"+filename+"_"+type, type, colors[i], over_time_value)
            plt.xlabel("#gates applied")
            plt.ylabel("#nodes")
            plt.legend(prop={'size':9})
            plt.yscale("log")
            plt.title("Grover's search algorithm: "+type)
        plt.savefig('plot/'+filename+"/"+filename+"_"+str(over_time_value)+".png", dpi=200)
        plt.clf()
        plot_time(filename, types, colors, start_value)
