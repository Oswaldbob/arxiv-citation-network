import logging
from configparser import ConfigParser
import os
import json

local_config = ConfigParser()
local_config.read(os.path.join(os.path.dirname(__file__), "config.ini"))


def get_logger(log_name):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
    )
    return logging.getLogger(log_name)


def get_meta():
    return local_config["USER"]["meta"]


# Get logger for util functions below
log = get_logger("utils")


def load_metadata(filename):
    log.info("Start reading {}".format(filename))
    with open(os.path.join(get_meta(), filename)) as f:
        data = json.load(f)

    return data


def save_metadata(data, filename):
    filename = os.path.join(get_meta(), filename)
    log.info("Start saving {}".format(filename))
    with open(filename, 'w+') as f:
        json.dump(data, f)


def remove_version_ending(arxiv_id):
    return arxiv_id.rsplit("v", 1)[0]


def get_loop_stats(object_of_for_loop, n):
    # Stats for loop counter
    entries = len(object_of_for_loop)
    counter_mark = entries // n
    return entries, counter_mark


def update_counter(counter, counter_mark, entries, n, logger):
    # Code for counter
    if (counter % counter_mark == 0) or (counter == entries - 1):
        nr = counter // counter_mark
        if counter == entries - 1:
            nr = n
        logger.info("Processed {} entries so far. {}/{}".format(counter, nr, n))


def arxiv_filename_to_id(name):
    """ Convert filepath name of ArXiv file to ArXiv ID """
    if '.' in name:  # new  ID
        return name

    split = name.split("_")
    return "/".join(split)
