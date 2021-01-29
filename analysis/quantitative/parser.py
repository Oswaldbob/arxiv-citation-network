import os
import json

META = "../../important_data/"


def load_metadata(filename):
    with open(os.path.join(META, filename)) as f:
        data = json.load(f)

    return data


parsed_100k = load_metadata("parsed_sampled_100k.json")

n = 100000
number_matched = len(parsed_100k)

# Collect all references
tmp_list = []
for key, value in parsed_100k.items():
    for ref in value:
        tmp_list.append(ref["title"])

# Count references
number_references_overall = len(tmp_list)
number_references_unique = len(set(tmp_list))

print("[Parser] Matched {} ({:.2%}); References-Overall: {}; References-Unique: {} (Unique-%: {:.2%});".format(
    number_matched, number_matched / n, number_references_overall,
    number_references_unique, number_references_unique / number_references_overall)
)
