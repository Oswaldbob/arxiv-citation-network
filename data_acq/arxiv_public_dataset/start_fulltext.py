from arxiv_public_dataset.fulltext import fulltext
from configparser import ConfigParser
import os
import multiprocessing
import glob
import shutil
import log_config_util

log = log_config_util.get_logger("fulltext")

PDF_OUT = log_config_util.get_pdfs_out()
FULLTXT_OUT = log_config_util.get_fulltext_out()


def initialize_fulltext(number_of_processes=None, timelimit=fulltext.TIMELIMIT):
    """

    :param number_of_processes: inti
        set number of process, optional, default is cpu count
    :param timelimit: int
        timelimit for subprocess call, default 120 sec
    """
    if number_of_processes:
        processes = int(number_of_processes)
    else:
        processes = multiprocessing.cpu_count()

    log.info("Start convert PDF")
    # Run fulltext to convert pdfs in tardir into *.txt
    converts = fulltext.convert_directory_parallel(
        PDF_OUT, FULLTXT_OUT, processes=processes, timelimit=timelimit
    )

    log.info("Start moving txt files")
    txtfiles = glob.glob('{}/*.txt'.format(PDF_OUT))
    for tf in txtfiles:
        shutil.move(tf, os.path.join(FULLTXT_OUT, os.path.basename(tf)))
    log.info("Clean up")
    txtfiles = glob.glob('{}/*.*txt'.format(PDF_OUT))
    for tf in txtfiles:
        os.remove(tf)
