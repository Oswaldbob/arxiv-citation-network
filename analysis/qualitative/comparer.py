import os
import json
import random

META = "../../important_data/"
N = 10000


def load_metadata(filename):
    print("Start reading " + filename)
    with open(os.path.join(META, filename)) as f:
        data = json.load(f)

    return data


def remove_version_ending(arxiv_id):
    return arxiv_id.rsplit("v", 1)[0]


def format_name_to_id(name):
    return ''.join(name.split()).lower()


def path_to_id(name):
    """ Convert filepath name of ArXiv file to ArXiv ID """
    if '.' in name:  # new  ID
        return name

    split = name.split("_")
    return "/".join(split)


valid_aids = set(list(map(remove_version_ending, load_metadata("sampled_aids_100k.json"))))
arxiv_metadata = load_metadata("arxiv_id_to_doi_title.json")

# Get ground truth
print("Get Ground truth")
# Filter mag data to only include ID from the sampled 100k and which have an DOI
mag_gt_overall = {key: value for key, value in load_metadata("aid_to_ref_magids.json").items()
                  if ((key in valid_aids) and (arxiv_metadata[key][0]))}
# Add empty references
for key in load_metadata("aids_without_ref.json"):
    if (key in valid_aids) and (arxiv_metadata[key][0]):
        mag_gt_overall[key] = []

# Sample 10k
random.seed("Random Seed for similar results upon rerunning the code")
gt_keys = set(random.sample(list(mag_gt_overall.keys()), N))

# Build sampled_gt
mag_data = load_metadata("magid_to_data.json")

# Get (title,arxiv_id) for all references entries by MAG data
gt_aid_to_data = {key: [(mag_data[ref_mag_id][2], mag_data[ref_mag_id][3]) for ref_mag_id in mag_gt_overall[key]]
                  for key in gt_keys}

gt_len = len(gt_aid_to_data)
gt_overall_references = sum([len(value) for key, value in gt_aid_to_data.items()])

# Get Bierbaum Work
print("Get Bierbaum data")
bierbaum_overall = load_metadata("merged_internal-citations.json")
bierbaum_compare_with_version = {key: value for key, value in bierbaum_overall.items() if
                                 remove_version_ending(key) in gt_keys}
bierbaum_compare = {}
for key, value in bierbaum_compare_with_version.items():
    aid_without_version = remove_version_ending(key)
    arxiv_citations_without_version = [remove_version_ending(tmp_aid) for tmp_aid in value]
    bierbaum_compare[aid_without_version] = arxiv_citations_without_version

# Compare Bierbaum Work
print("Compare Bierbaum data")
bb_len = len(bierbaum_compare)
bb_overall_references = sum([len(value) for key, value in bierbaum_compare.items()])
bb_hit = 0
bb_miss = 0
bb_self = 0
# Compare based only arxiv IDs as bierbaum's work only has arxiv IDs
arxiv_metadata_keys = set(arxiv_metadata.keys())
for arxiv_id, references in bierbaum_compare.items():

    # Get values of Ground truth
    gt_references = gt_aid_to_data[arxiv_id]
    gt_arxiv_ids = set([data[1] for data in gt_references if data[1]])
    gt_titles = set([format_name_to_id(data[0]) for data in gt_references])

    # Check compliance
    for ref_aid in references:
        # Skip in case of self reference
        if ref_aid == arxiv_id:
            bb_self += 1
            continue

        if ref_aid in gt_arxiv_ids:
            bb_hit += 1
            continue

        if (ref_aid in arxiv_metadata_keys) and (format_name_to_id(arxiv_metadata[ref_aid][1]) in gt_titles):
            bb_hit += 1
            continue

        # Unable to match the reference found by bierbaum to a reference in the ground truth
        bb_miss += 1

# Compare parser results
print("Get Parser data")
parsed_100k = load_metadata("parsed_sampled_100k.json")
parsed_sampled_without_version = {}
for key, p_references in parsed_100k.items():
    # Remove version
    aid_no_version = remove_version_ending(key)
    # Make _ to / as its coming from file names
    aid_fixed = path_to_id(aid_no_version)

    if aid_fixed in gt_keys:
        parsed_sampled_without_version[aid_fixed] = [format_name_to_id(ref["title"]) for ref in p_references]

print("Compare Parser data")
p_len = len(parsed_sampled_without_version)
p_overall_references = sum([len(value) for key, value in parsed_sampled_without_version.items()])
p_hit = 0
p_miss = 0
p_self = 0

# Compare based only arxiv IDs as bierbaum's work only has arxiv IDs
for arxiv_id, references in parsed_sampled_without_version.items():

    # Get values of Ground truth
    gt_references = gt_aid_to_data[arxiv_id]
    gt_titles = set([format_name_to_id(data[0]) for data in gt_references])

    # Check compliance
    for ref_title in references:
        # Skip in case of self reference
        if (arxiv_id in arxiv_metadata_keys) and (ref_title == format_name_to_id(arxiv_metadata[arxiv_id][1])):
            p_self += 1
            continue

        if ref_title in gt_titles:
            p_hit += 1
            continue

        # Unable to match the reference found by bierbaum to a reference in the ground truth
        p_miss += 1

print("\n[Ground Truth (GT) MAG] Entries: {}; Overall references {}".format(gt_len, gt_overall_references))

print(("[Bierbaum] Entries: {} (%-of-GT: {:.2%}); Overall references {} (%-of-GT: {:.2%}); " +
       "Found {} of GT references ({:.2%}). Found {} references not in GT (%-of-Bierbaum-Refs: {:.2%}). Self-references: {}").format(
    bb_len, bb_len / gt_len, bb_overall_references, bb_overall_references / gt_overall_references,
    bb_hit, bb_hit / gt_overall_references, bb_miss, bb_miss / bb_overall_references, bb_self)
)

print(("[Parser] Entries: {} (%-of-GT: {:.2%}); Overall references {} (%-of-GT: {:.2%}); " +
       "Found {} of GT references ({:.2%}). Found {} references not in GT (%-of-Parser-Refs: {:.2%}). Self-references: {}").format(
    p_len, p_len / gt_len, p_overall_references, p_overall_references / gt_overall_references,
    p_hit, p_hit / gt_overall_references, p_miss, p_miss / p_overall_references, p_self)
)
