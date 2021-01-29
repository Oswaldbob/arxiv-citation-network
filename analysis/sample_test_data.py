# A short script to sample 100000 arxiv IDs which are treated as test data for comparison of different methods
import os
import json
import random

# Sample number
n = 100000

important_data_base = "../important_data/"
with open(os.path.join(important_data_base, "merged_internal-citations.json")) as f:
    data = json.load(f)

# Get a set of all downloaded and successfully converted arxiv IDs across all partitions
aids = list(data.keys())
# As of 1.1.2021, this should be: 1791470 (same number as output from data_acq combined)
print("Number of successfully converted and downloaded PDFs: {}".format(len(aids)))

# Sample 100k
sampled_data = random.sample(aids, n)

with open(os.path.join(important_data_base, "sampled_aids_100k.json"), 'w+') as f:
    json.dump(sampled_data, f)
