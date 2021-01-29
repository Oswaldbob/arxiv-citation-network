import logging
from configparser import ConfigParser
import os

local_config = ConfigParser()
local_config.read(os.path.join(os.path.dirname(__file__), "config.ini"))


def get_logger(log_name):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
    )
    return logging.getLogger(log_name)


def get_science_parse_jar():
    return local_config["PATHS"]["science_parse_jar"]


def get_origin_pdfs():
    return local_config["PATHS"]["origin_pdfs"]


def get_pdfs_to_parse():
    return local_config["PATHS"]["pdfs_to_parse"]


def get_aids_to_copy():
    return local_config["PATHS"]["aids_to_copy"]


def get_parsing_results():
    return local_config["PATHS"]["parsing_results"]


def get_extracted_references():
    return local_config["PATHS"]["extracted_references"]
