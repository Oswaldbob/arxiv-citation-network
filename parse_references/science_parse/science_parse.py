import os
import time

from parse_references import log_config_util


start = time.time()

os.system('java -Xmx6G -jar {} {} -o {}'.format(
    log_config_util.get_science_parse_jar(),
    log_config_util.get_pdfs_to_parse(),
    log_config_util.get_parsing_results()))

print(time.time() - start)
