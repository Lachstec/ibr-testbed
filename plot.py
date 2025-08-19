import json
import glob
import numpy as np 
import matplotlib.pyplot as plt
from pathlib import Path

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

#baseline_mean = baseline_array.mean(axis=0) / 1000
#baseline_std = baseline_array.std(axis=0)
#p10000_mean = p10000_array.mean(axis=0)
#p10000_std = p10000_array.std(axis=0)

interval_len = 1.0
time_axis = np.arange(max_len) * interval_len

fig, axes = plt.subplots(1, 3, figsize=(10,5))

l1, = axes[0].plot(time_axis, real_mean / 1000, label="real / 1000", color="blue")
l2, = axes[0].plot(time_axis, mib1_mean, label="No PBR", color="orange")
axes[0].set_xlabel("Time (s)")
axes[0].set_ylabel("Throughput (Mbps)")

axes[1].plot(time_axis, real_mean * 0.002, label="real / 1000", color="blue")
l3, = axes[1].plot(time_axis, mib2_mean, label="PBR - One Hop", color="green")
axes[1].set_xlabel("Time (s)")
axes[1].set_ylabel("Throughput (Mbps)")

axes[2].plot(time_axis, real_mean * 0.007, label="real / 1000", color="blue")
l4, = axes[2].plot(time_axis, mib7_mean, label="PBR - Two Hops", color="red")
axes[2].set_xlabel("Time (s)")
axes[2].set_ylabel("Throughput (Mbps)")

fig.legend(
        handles=[l1, l2, l3, l4],
        loc="lower center",
        ncol=3,
)

fig.tight_layout(rect=[0, 0.15, 1, 0.95])  # leave ~12% space at the top
fig.suptitle("Throughput over Time")

fig.savefig("throughput_overlay.png", dpi=300)
fig.savefig("throughput_overlay.pdf")
plt.close()

#plt.figure(figsize=(8,5))
#plt.plot(time_axis, baseline_mean, label="real / 1000", color="blue")
#plt.fill_between(time_axis, baseline_mean - baseline_std, baseline_mean + baseline_std, color="blue", alpha=0.2)
#plt.plot(time_axis, p10000_mean, label="Containerlab", color="orange")
#plt.fill_between(time_axis, p10000_mean - p10000_std, p10000_mean + p10000_std, color="orange", alpha=0.2)
#plt.xlabel("Time (s)")
#plt.ylabel("Throughput (Mbps)")
#plt.title("Throughput over Time (Overlay)")
#plt.legend()
#plt.tight_layout()

#plt.savefig("throughput_overlay.png", dpi=300)
#plt.savefig("throughput_overlay.pdf")
#plt.close()

