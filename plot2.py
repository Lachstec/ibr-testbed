import json
import glob
import numpy as np 
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import MaxNLocator

def load_iperf_data(files):
    runs = []
    for file in files:
        with open(file) as f:
            data = json.load(f)
        try:
            intervals = data['intervals']
            bps = [iv['sum']['bits_per_second'] / 1e6 for iv in intervals]
            runs.append(bps)
        except KeyError:
            print(f"Error: {file} not containing expected data")
    return runs

baseline_files = sorted(glob.glob("localThroughput/*.log"))
mib1_files = sorted(glob.glob("baseline/baseline/*.json"))
mib2_files = sorted(glob.glob("pbr/*.json"))
mib7_files = sorted(glob.glob("pbr2/*.json"))

real_runs = load_iperf_data(baseline_files)
mib1_runs = load_iperf_data(mib1_files)
mib2_runs = load_iperf_data(mib2_files)
mib7_runs = load_iperf_data(mib7_files)

max_len = min(min(len(r) for r in real_runs), min(len(r) for r in mib1_runs))
real_runs = [r[:max_len] for r in real_runs]
mib1_runs = [r[:max_len] for r in mib1_runs]
mib2_runs = [r[:max_len] for r in mib2_runs]
mib7_runs = [r[:max_len] for r in mib7_runs]

real_array = np.array(real_runs)
mib1_array = np.array(mib1_runs)
mib2_array = np.array(mib2_runs)
mib7_array = np.array(mib7_runs)

real_mean = real_array.mean(axis=0)
mib1_mean = mib1_array.mean(axis=0)
mib2_mean = mib2_array.mean(axis=0)
mib7_mean = mib7_array.mean(axis=0)

interval_len = 1.0
time_axis = np.arange(max_len) * interval_len

# --- Make the figure shorter (height reduced ~40%) ---
# Original: figsize=(10, 5). New: keep width similar but reduce height.
fig, axes = plt.subplots(1, 3, figsize=(12, 3))  # try (12,3) for ~40% shorter

# common font sizes (smaller because figure is shorter)
label_fontsize = 10
tick_fontsize = 8
title_fontsize = 12
legend_fontsize = 9

# Left subplot
l1, = axes[0].plot(time_axis, real_mean / 1000, label="real / 1000", color="blue")
l2, = axes[0].plot(time_axis, mib1_mean, label="No PBR", color="orange")
axes[0].set_xlabel("Time (s)", fontsize=label_fontsize)
# force a single-line horizontal ylabel and push it left of the axis so it doesn't collide
axes[0].set_ylabel("Throughput (Mbps)", fontsize=label_fontsize)
#axes[0].yaxis.set_label_coords(-0.22, 0.5)   # (x, y) in axis coordinates
axes[0].tick_params(axis='both', labelsize=tick_fontsize)

# Middle subplot
axes[1].plot(time_axis, real_mean * 0.002, label="real / 1000", color="blue")
l3, = axes[1].plot(time_axis, mib2_mean, label="PBR - One Hop", color="green")
axes[1].set_xlabel("Time (s)", fontsize=label_fontsize)
axes[1].set_ylabel("Throughput (Mbps)", fontsize=label_fontsize)
#axes[1].yaxis.set_label_coords(-0.22, 0.5)
axes[1].tick_params(axis='both', labelsize=tick_fontsize)

# Right subplot
axes[2].plot(time_axis, real_mean * 0.007, label="real / 1000", color="blue")
l4, = axes[2].plot(time_axis, mib7_mean, label="PBR - Two Hops", color="red")
axes[2].set_xlabel("Time (s)", fontsize=label_fontsize)
axes[2].set_ylabel("Throughput (Mbps)", fontsize=label_fontsize)
#axes[2].yaxis.set_label_coords(-0.22, 0.5)
axes[2].tick_params(axis='both', labelsize=tick_fontsize)

for ax in axes:
    ax.yaxis.set_major_locator(MaxNLocator(nbins=4, prune='both'))  # try 3,4,5...
    ax.tick_params(axis='y', labelsize=tick_fontsize)

# centralized legend below plots ...
fig.legend(
    handles=[l1, l2, l3, l4],
    labels=["real / 1000", "No PBR", "PBR - One Hop", "PBR - Two Hops"],
    loc="lower center",
    bbox_to_anchor=(0.5, -0.06),
    ncol=4,
    fontsize=legend_fontsize,
    frameon=True
)

# smaller top title, placed to avoid overlapping with axes in the reduced height
fig.suptitle("Throughput over Time", fontsize=title_fontsize)
# adjust spacing: bring subplots up a bit and leave space for the legend
plt.subplots_adjust(left=0.12, right=0.98, top=0.88, bottom=0.20, wspace=0.35)

fig.savefig("throughput_overlay_shorter.png", dpi=300, bbox_inches='tight')
fig.savefig("throughput_overlay_shorter.pdf", bbox_inches='tight')
plt.close()