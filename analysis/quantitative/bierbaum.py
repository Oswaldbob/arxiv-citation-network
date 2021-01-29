import os
import json

META = "../../important_data/"


def load_metadata(filename):
    with open(os.path.join(META, filename)) as f:
        data = json.load(f)

    return data


def remove_version_ending(arxiv_id):
    return arxiv_id.rsplit("v", 1)[0]


bierbaum_overall = load_metadata("merged_internal-citations.json")
# Get sampled ID without version
valid_aids = set(list(map(remove_version_ending, load_metadata("sampled_aids_100k.json"))))

# Remove version for comparison (this might reduce number of unique refs as sometimes multiple versions are found)
bierbaum_without_version = {}
for key, value in bierbaum_overall.items():
    aid_without_version = remove_version_ending(key)
    arxiv_citations_without_version = list(map(remove_version_ending, value))
    bierbaum_without_version[aid_without_version] = arxiv_citations_without_version

# Get list of 100k sampled from bierbaum output on whole dataset
bierbaum_100k = {key: value for key, value in bierbaum_without_version.items() if key in valid_aids}

n = 100000
number_matched = len(bierbaum_100k)

# Collect all references
tmp_list = []
for key, value in bierbaum_100k.items():
    for ref in value:
        tmp_list.append(ref)

# Count references
number_references_overall = len(tmp_list)
number_references_unique = len(set(tmp_list))

print("[Bierbaum] Matched {} ({:.2%}); References-Overall: {}; References-Unique: {} (Unique-%: {:.2%});".format(
    number_matched, number_matched / n, number_references_overall,
    number_references_unique, number_references_unique / number_references_overall)
)
