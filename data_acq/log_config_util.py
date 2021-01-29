import logging
from configparser import ConfigParser
import os

local_config = ConfigParser()
local_config.read(os.path.join(os.path.dirname(__file__), "config.ini"))


def get_logger(log_name):
    if "log_to_file" in local_config["USER"] and local_config["USER"]["log_to_file"] == "yes":
        logging.basicConfig(
            filename=os.path.join(local_config["USER"]["log_out"], "data_acq.log"),
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
        )
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
        )
    return logging.getLogger(log_name)


def get_meta_out():
    return local_config["USER"]["meta_out"]


def get_pdfs_out():
    return local_config["USER"]["pdfs_out"]


def get_fulltext_out():
    return local_config["USER"]["fulltext_out"]
