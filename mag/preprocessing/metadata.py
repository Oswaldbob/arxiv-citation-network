import subprocess
import json
import os
import log_config_util
import gzip

log = log_config_util.get_logger("metadata")
META_OUT = log_config_util.get_meta_out()


def download_metadata():
    """Not used as version of bucket is outdated"""
    log.info("Start Download [This takes a while]")
    result = subprocess.run(["gsutil", "cp", "gs://arxiv-dataset/metadata-v5/arxiv-metadata-oai.json", META_OUT],
                            capture_output=True,
                            text=True)
    result.check_returncode()  # If return code is non-zero, raise a CalledProcessError.
    log.info("Metadata from Bucket has been downloaded")


def process_metadata():
    # Parse line by line
    id_doi_dict = {}
    log.info("Start reading JSON line by line")
    with open(os.path.join(META_OUT, "arxiv-metadata-oai-snapshot.json")) as f:
        for line in f:
            parsed_line = json.loads(line)
            id_doi_dict[parsed_line["id"]] = [parsed_line["doi"], parsed_line["title"]]

    # Get amount of empty doi entries and remove empty values
    empty_counter = 0
    for key, value in id_doi_dict.items():
        if not value[0]:
            empty_counter += 1
            continue

    # log some stats
    length = len(id_doi_dict)
    doi_empty = empty_counter / length
    log.info("Stats about metadata: Entries: {}, DOI-Empty-% {}".format(length, doi_empty))

    return id_doi_dict


def save_metadata(id_doi_dict):
    # Adapted from arxiv public dataset .gz json dump
    filename = os.path.join(META_OUT, "arxiv_id_to_doi_title.json.gz")
    log.info('Saving to "{}"'.format(filename))
    with gzip.open(filename, 'wb+') as fn:
        fn.write(json.dumps(id_doi_dict).encode('utf-8'))
