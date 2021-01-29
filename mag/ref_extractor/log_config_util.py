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


def get_meta():
    return local_config["USER"]["meta"]


def get_mag_base():
    return local_config["USER"]["mag_base"]
