from configparser import ConfigParser
import os
import json

local_config = ConfigParser()
local_config.read("./config.ini")

# Load Data
path_to_file_p1 = os.path.join(local_config["USER"]["download_in"], "internal-citations_p1.json")

path_to_file_p2 = os.path.join(local_config["USER"]["download_in"], "internal-citations_p2.json")

print("Load Data")
with open(path_to_file_p1) as json_file:
    data_1 = json.load(json_file)

with open(path_to_file_p2) as json_file:
    data_2 = json.load(json_file)

print("Combine Data")
data_1.update(data_2)

print("Dump Data")
with open(os.path.join(local_config["USER"]["download_in"], "merged_internal-citations.json"), "w") as outfile:
    json.dump(data_1, outfile)
