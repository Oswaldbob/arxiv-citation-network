#! /usr/bin/env python
# adapted from https://github.com/mattbierbaum/arxiv-public-datasets/blob/master/arxiv_public_data/internal_citations.py
import re
import gzip
import json
import math
from multiprocessing import Pool
import os
from arxiv_public_dataset.internal_citations.regex_arxiv import REGEX_ARXIV_FLEXIBLE, clean
import log_config_util

log = log_config_util.get_logger("internal_citations")
DIR_OUTPUT = log_config_util.get_meta_out()
DIR_FULLTEXT = log_config_util.get_fulltext_out()

RE_FLEX = re.compile(REGEX_ARXIV_FLEXIBLE)


def path_to_id(path):
    """ Convert filepath name of ArXiv file to ArXiv ID """
    name = os.path.splitext(os.path.basename(path))[0]
    if '.' in name:  # new  ID
        return name

    split = name.split("_")
    return "/".join(split)


def all_articles(directory=DIR_FULLTEXT):
    """ Find all *.txt files in directory """
    out = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if 'txt' in f:
                out.append(os.path.join(root, f))
    return out


def extract_references(filename, pattern=RE_FLEX):
    """
    Parameters
    ----------
        filename : str
            name of file to search for pattern
        pattern : re pattern object
            compiled regex pattern

    Returns
    -------
        citations : list
            list of found arXiv IDs
    """
    out = []
    with open(filename, 'r') as fn:
        txt = fn.read()

        for matches in pattern.findall(txt):
            out.extend([clean(a) for a in matches if a])
    return list(set(out))


def citation_list_inner(articles):
    """ Find references in all the input articles
    Parameters
    ----------
        articles : list of str
            list of paths to article text
    Returns
    -------
        citations : dict[arXiv ID] = list of arXiv IDs
            dictionary of articles and their references
    """
    cites = {}
    for i, article in enumerate(articles):
        if i > 0 and i % 1000 == 0:
            log.info('Completed {} articles'.format(i))
        try:
            refs = extract_references(article)
            cites[path_to_id(article)] = refs
        except:
            log.error("Error in {}".format(article))
            continue
    return cites


def citation_list_parallel(N=8):
    """
    Split the task of checking for citations across some number of processes
    Parameters
    ----------
        N : int
            number of processes
    Returns
    -------
        citations : dict[arXiv ID] = list of arXiv IDs
            all arXiv citations in all articles
    """
    articles = all_articles()
    log.info('Calculating citation network for {} articles'.format(len(articles)))

    pool = Pool(N)

    A = len(articles)
    divs = list(range(0, A, math.ceil(A / N))) + [A]
    chunks = [articles[s:e] for s, e in zip(divs[:-1], divs[1:])]

    cites = pool.map(citation_list_inner, chunks)

    allcites = {}
    for c in cites:
        allcites.update(c)
    return allcites


def default_filename():
    return os.path.join(DIR_OUTPUT, 'internal-citations.json.gz')


def save_to_default_location(citations):
    filename = default_filename()

    log.info('Saving to "{}"'.format(filename))
    with gzip.open(filename, 'wb') as fn:
        fn.write(json.dumps(citations).encode('utf-8'))
