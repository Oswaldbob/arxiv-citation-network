# Main file to start scripts and manage config
import pdfs
import os
import sys
from arxiv_public_dataset import start_fulltext, start_int_cite
import log_config_util

# Set python base path to find logger utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
log = log_config_util.get_logger("main")

collect_metadata = True
download = True
convert = True
build_intra_cites = True

parallel_download = True
start_index = 0
pdf_max_size = 10
number_of_processes = None

try:
    # Main Script parts
    if collect_metadata:
        pdfs.get_pdf_metadata()

    if download:
        # Get Downloaded so far
        log.info("Started checking what was downloaded so far [This may take a while]")
        downloaded_ids = pdfs.downloaded_so_far()

        # Get slice for download
        log.info("Started selecting entries to download")
        pdf_metadata_to_download, end_index = pdfs.select_pdfs_to_download(start_index, pdf_max_size, downloaded_ids)
        size = sum(int(entry[0]) for entry in pdf_metadata_to_download)
        log.info("Size of selected (non-downloaded) PDFs in GB: {}. Number of PDFs: {}".format(size / (1e+9), len(
            pdf_metadata_to_download)))

        # Is the same number as above (if not at end of list or some are already downloaded)
        # because the end index is the next pdf due to start from 0
        log.info("End Index of Slice is: {}.".format(end_index))

        if len(pdf_metadata_to_download) != 0:
            # Store slice of data for usage in download
            log.info("Store download lists")
            pdfs.store_pdf_list(pdf_metadata_to_download)

            # Start downloading
            error_raised = pdfs.download_pdf(parallel_download)
            if error_raised:
                raise RuntimeError("Gsutil related error")
        else:
            log.info("Nothing to download, skip downloading step.")

    if convert:
        # Convert
        start_fulltext.initialize_fulltext(number_of_processes=number_of_processes)

    if build_intra_cites:
        start_int_cite.initialize_intra_cite(number_of_processes=number_of_processes)

    log.info("Finished processing")

except Exception as e:
    log.exception("Fatal error in main loop. Aboard any action")
