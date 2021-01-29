# adapted from https://github.com/mattbierbaum/arxiv-public-datasets/blob/master/bin/cocitations.py
from arxiv_public_dataset.internal_citations import internal_citations
import multiprocessing
import log_config_util

log = log_config_util.get_logger("internal_citations")


def initialize_intra_cite(number_of_processes=None):
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

    log.info("Start collecting citation list")
    cites = internal_citations.citation_list_parallel(N=processes)
    log.info("Start Saving citation list")
    internal_citations.save_to_default_location(cites)
