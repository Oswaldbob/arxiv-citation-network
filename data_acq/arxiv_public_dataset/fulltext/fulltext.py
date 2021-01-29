# This is a file for which the code mainly comes from https://github.com/mattbierbaum/arxiv-public-datasets - just put together a bit differently to fit our situation
import os
import re
import glob
import shlex
from functools import partial
from subprocess import check_call, CalledProcessError, TimeoutExpired, PIPE
from multiprocessing import Pool
from arxiv_public_dataset.fulltext import fixunicode
import log_config_util

log = log_config_util.get_logger("fulltext")
FULLTXT_OUT = log_config_util.get_fulltext_out()

TIMELIMIT = 2 * 60
PDFTOTEXT = 'pdftotext'
PDF2TXT = 'pdf2txt.py'


def reextension(filename: str, extension: str) -> str:
    """ Give a filename a new extension """
    name, _ = os.path.splitext(filename)
    return '{}.{}'.format(name, extension)


def process_timeout(cmd, timeout):
    return check_call(cmd, timeout=timeout, stdout=PIPE, stderr=PIPE)


def average_word_length(txt):
    """
    Gather statistics about the text, primarily the average word length
    Parameters
    ----------
    txt : str
    Returns
    -------
    word_length : float
        Average word length in the text
    """
    # txt = re.subn(RE_REPEATS, '', txt)[0]
    nw = len(txt.split())
    nc = len(txt)
    avgw = nc / (nw + 1)
    return avgw


def run_pdftotext(pdffile: str, timelimit: int = TIMELIMIT) -> str:
    """
    Run pdftotext on PDF file for extracted plain text
    Parameters
    ----------
    pdffile : str
        Path to PDF file
    timelimit : int
        Amount of time to wait for the process to complete
    Returns
    -------
    output : str
        Full plain text output
    """
    log.debug('Running {} on {}'.format(PDFTOTEXT, pdffile))
    tmpfile = reextension(pdffile, 'pdftotxt')

    cmd = '{cmd} {pdf} {output}'.format(
        cmd=PDFTOTEXT, pdf=pdffile, output=tmpfile
    )
    cmd = shlex.split(cmd)
    output = process_timeout(cmd, timeout=timelimit)

    with open(tmpfile) as f:
        return f.read()


def run_pdf2txt(pdffile: str, timelimit: int = TIMELIMIT, options: str = ''):
    """
    Run pdf2txt to extract full text
    Parameters
    ----------
    pdffile : str
        Path to PDF file
    timelimit : int
        Amount of time to wait for the process to complete
    Returns
    -------
    output : str
        Full plain text output
    """
    log.debug('Running {} on {}'.format(PDF2TXT, pdffile))
    tmpfile = reextension(pdffile, 'pdf2txt')

    cmd = '{cmd} {options} -o {output} {pdf}'.format(
        cmd=PDF2TXT, options=options, output=tmpfile, pdf=pdffile
    )
    cmd = shlex.split(cmd)
    output = process_timeout(cmd, timeout=timelimit)

    with open(tmpfile) as f:
        return f.read()


def run_pdf2txt_A(pdffile: str, **kwargs) -> str:
    """
    Run pdf2txt with the -A option which runs 'positional analysis on images'
    and can return better results when pdf2txt combines many words together.
    Parameters
    ----------
    pdffile : str
        Path to PDF file
    kwargs : dict
        Keyword arguments to :func:`run_pdf2txt`
    Returns
    -------
    output : str
        Full plain text output
    """
    return run_pdf2txt(pdffile, options='-A', **kwargs)


def fulltext(pdffile: str, timelimit: int = TIMELIMIT):
    """
    Given a pdf file, extract the unicode text and run through very basic
    unicode normalization routines. Determine the best extracted text and
    return as a string.
    Parameters
    ----------
    pdffile : str
        Path to PDF file from which to extract text
    timelimit : int
        Time in seconds to allow the extraction routines to run
    Returns
    -------
    fulltext : str
        The full plain text of the PDF
    """
    if not os.path.isfile(pdffile):
        raise FileNotFoundError(pdffile)

    if os.stat(pdffile).st_size == 0:  # file is empty
        raise RuntimeError('"{}" is an empty file'.format(pdffile))

    try:
        output = run_pdftotext(pdffile, timelimit=timelimit)
        # output = run_pdf2txt(pdffile, timelimit=timelimit)
    except (TimeoutExpired, CalledProcessError, RuntimeError) as e:
        output = run_pdf2txt(pdffile, timelimit=timelimit)
        # output = run_pdftotext(pdffile, timelimit=timelimit)

    output = fixunicode.fix_unicode(output)
    # output = stamp.remove_stamp(output, split=STAMP_SEARCH_LIMIT)
    wordlength = average_word_length(output)

    if wordlength <= 45:
        return output

    output = run_pdf2txt_A(pdffile, timelimit=timelimit)
    output = fixunicode.fix_unicode(output)
    # output = stamp.remove_stamp(output, split=STAMP_SEARCH_LIMIT)
    wordlength = average_word_length(output)

    if wordlength > 45:
        raise RuntimeError(
            'No accurate text could be extracted from "{}"'.format(pdffile)
        )

    return output


def sorted_files(globber: str):
    """
    Give a globbing expression of files to find. They will be sorted upon
    return.  This function is most useful when sorting does not provide
    numerical order,
    e.g.:
        9 -> 12 returned as 10 11 12 9 by string sort
    In this case use num_sort=True, and it will be sorted by numbers in the
    string, then by the string itself.
    Parameters
    ----------
    globber : str
        Expression on which to search for files (bash glob expression)
    """
    files = glob.glob(globber)
    files.sort()

    allfiles = []

    for fn in files:
        nums = re.findall(r'\d+', fn)
        data = [int(n) for n in nums] + [fn]
        allfiles.append(data)

    allfiles = sorted(allfiles, key=lambda x: x[:-1])
    return [f[-1] for f in allfiles]


def convert_directory(path: str, timelimit: int = TIMELIMIT):
    """
    Convert all pdfs in a given `path` to full plain text. For each pdf, a file
    of the same name but extension .txt will be created. If that file exists,
    it will be skipped.
    Parameters
    ----------
    path : str
        Directory in which to search for pdfs and convert to text
    Returns
    -------
    output : list of str
        List of converted files
    """
    outlist = []

    globber = os.path.join(path, '*.pdf')
    pdffiles = sorted_files(globber)

    log.info('Searching "{}"...'.format(globber))
    log.info('Found: {} pdfs'.format(len(pdffiles)))

    for pdffile in pdffiles:
        txtfile = reextension(pdffile, 'txt')

        if os.path.exists(txtfile):
            continue

        # we don't want this function to stop half way because of one failed
        # file so just charge onto the next one
        try:
            text = fulltext(pdffile, timelimit)
            with open(txtfile, 'w') as f:
                f.write(text)
        except Exception as e:
            log.error("Conversion failed for '{}'".format(pdffile))
            log.exception(e)
            continue

        outlist.append(pdffile)
    return outlist


def convert_directory_parallel(path: str, path_output: str, processes: int, timelimit: int = TIMELIMIT):
    """
    Convert all pdfs in a given `path` to full plain text. For each pdf, a file
    of the same name but extension .txt will be created. If that file exists,
    it will be skipped.
    Parameters
    ----------
    path : str
        Directory in which to search for pdfs and convert to text
    Returns
    -------
    output : list of str
        List of converted files
    """
    globber = os.path.join(path, '*.pdf')
    pdffiles = sorted_files(globber)

    ## This is custom code (not from Bierbaum) to avoid that files that are stored in another directory are not considered and would be redownloaded
    # Get txt files in output dir
    txtfiles = glob.glob('{}/*.txt'.format(path_output))
    # Get names of all txt files
    txtfiles = [filename for filepath in txtfiles if (filename := os.path.splitext(os.path.basename(filepath))[0])]
    # Filter all pdf files whose .txt version exit in the output dir
    txtfiles_set = set(txtfiles)
    convert_still_required = []
    for filepath_pdf in pdffiles:
        filename_with_ext = os.path.basename(filepath_pdf)
        filename = os.path.splitext(filename_with_ext)[0]
        if not (filename in txtfiles_set):
            convert_still_required.append(filepath_pdf)
    ## End of custom code

    log.info('Searching "{}"...'.format(globber))
    log.info('Found: {} pdfs. Still need to convert {} pdfs'.format(len(pdffiles), len(convert_still_required)))

    pool = Pool(processes=processes)
    result = pool.map(partial(convert_safe, timelimit=timelimit), convert_still_required)
    pool.close()
    pool.join()


def convert_safe(pdffile: str, timelimit: int = TIMELIMIT):
    """ Conversion function that never fails """
    try:
        convert(pdffile, timelimit=timelimit)
    except Exception as e:
        log.error('File conversion failed for {}: {}'.format(pdffile, e))


def convert(path: str, skipconverted=True, timelimit: int = TIMELIMIT) -> str:
    """
    Convert a single PDF to text.
    Parameters
    ----------
    path : str
        Location of a PDF file.
    skipconverted : boolean
        Skip conversion when there is a text file already
    Returns
    -------
    str
        Location of text file.
    """
    if not os.path.exists(path):
        raise RuntimeError('No such path: %s' % path)
    outpath = reextension(path, 'txt')

    if os.path.exists(outpath):
        return outpath

    try:
        content = fulltext(path, timelimit)
        with open(outpath, 'w') as f:
            f.write(content)
    except Exception as e:
        msg = "Conversion failed for '%s': %s"
        log.error(msg, path, e)
        raise RuntimeError(msg % (path, e)) from e
    return outpath
