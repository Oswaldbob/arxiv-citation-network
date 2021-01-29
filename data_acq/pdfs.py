import subprocess
from packaging import version
from configparser import ConfigParser
import os
import csv
import glob
import shutil
import log_config_util

log = log_config_util.get_logger("pdf")

BUCKET_NAME = "arxiv-dataset"
# Read config.ini file
PDF_OUT = log_config_util.get_pdfs_out()
META_OUT = log_config_util.get_meta_out()
FILELISTS_OUT = os.path.join(META_OUT, "filelists")

# This data was collected by the function get_all_base_dir in utils.py (should not change in the future)
PDF_DIR_PATHS = ['arxiv/acc-phys/pdf', 'arxiv/adap-org/pdf', 'arxiv/alg-geom/pdf', 'arxiv/ao-sci/pdf',
                 'arxiv/arxiv/pdf', 'arxiv/astro-ph/pdf', 'arxiv/atom-ph/pdf', 'arxiv/bayes-an/pdf',
                 'arxiv/chao-dyn/pdf', 'arxiv/chem-ph/pdf', 'arxiv/cmp-lg/pdf', 'arxiv/comp-gas/pdf',
                 'arxiv/cond-mat/pdf', 'arxiv/cs/pdf', 'arxiv/dg-ga/pdf', 'arxiv/funct-an/pdf', 'arxiv/gr-qc/pdf',
                 'arxiv/hep-ex/pdf', 'arxiv/hep-lat/pdf', 'arxiv/hep-ph/pdf', 'arxiv/hep-th/pdf', 'arxiv/math-ph/pdf',
                 'arxiv/math/pdf', 'arxiv/mtrl-th/pdf', 'arxiv/nlin/pdf', 'arxiv/nucl-ex/pdf', 'arxiv/nucl-th/pdf',
                 'arxiv/patt-sol/pdf', 'arxiv/physics/pdf', 'arxiv/plasm-ph/pdf', 'arxiv/q-alg/pdf', 'arxiv/q-bio/pdf',
                 'arxiv/quant-ph/pdf', 'arxiv/solv-int/pdf', 'arxiv/supr-con/pdf']


def get_pdf_metadata():
    """
    Collects PDF metadata and exports it as a csv
    Format: size in bytes, directory, path, id, version
    """
    # Collect metadata
    len_metadata = 0
    nr_to_process = len(PDF_DIR_PATHS)

    path_to_output_file = os.path.join(META_OUT, "pdfs.csv")

    if os.path.exists(path_to_output_file):
        os.remove(path_to_output_file)

    for counter, dir in enumerate(PDF_DIR_PATHS, 1):
        log.info("Processing: {} #{}/{}".format(dir, counter, nr_to_process))
        metadata = get_pdf_data_per_dir(dir)
        len_metadata += len(metadata)

        # Tuple export adapted from https://stackoverflow.com/questions/15578331/save-list-of-ordered-tuples-as-csv
        with open(path_to_output_file, "a+") as out:
            csv_out = csv.writer(out)
            csv_out.writerows(metadata)

    log.info("Articles found and collected {}".format(len_metadata))


def get_pdf_data_per_dir(pdf_dir):
    """
    Get metadata about all pdfs on the bucket. Explicitly storing size, path and directory of pdf which are stored as json
    :return: List of tuples with format (size in bytes, directory, path, id, version)
    """
    result = subprocess.run(["gsutil", "ls", "-l", "gs://{}/{}/**.pdf".format(BUCKET_NAME, pdf_dir)],
                            capture_output=True,
                            text=True)
    result.check_returncode()  # If return code is non-zero, raise a CalledProcessError.
    lines = result.stdout.split("\n")
    lines = lines[:-2]

    # Create tuple with (size in bytes, directory, path, id, version)
    if pdf_dir == "arxiv/arxiv/pdf":
        # Here the name of the pdf is the ID
        metadata = [(splits[0], pdf_dir, splits[2], filename_and_version[0], filename_and_version[1])
                    for line in lines if
                    line and (splits := line.split()) and (
                        filename_and_version := splits[2].split("/")[-1][:-4].split("v"))]
    else:
        # ID is combination of dir and file name
        metadata = [(splits[0], pdf_dir, splits[2], "{}/{}".format(pdf_dir.split("/")[1], filename_and_version[0]),
                     filename_and_version[1])
                    for line in lines if line and (splits := line.split()) and (
                        filename_and_version := splits[2].split("/")[-1][:-4].split("v"))]

    # Find version duplicates
    dupl_dict = {}  # dict of {id: highest_version_number}
    for entry in metadata:
        if entry[3] not in dupl_dict:
            # float not integer as it seems that version like "1.1" is allowed for some pdfs
            # some version numbers have a/b in it
            dupl_dict[entry[3]] = version.parse(entry[4])
        else:
            if dupl_dict[entry[3]] < version.parse(entry[4]):
                dupl_dict[entry[3]] = version.parse(entry[4])

    # Clear metadata of version duplicates
    metadata = [entry for entry in metadata if version.parse(entry[4]) == dupl_dict[entry[3]]]

    return metadata


def get_stored_metadata():
    """
    Read the stored metadata
    :return: list of list of [size in bytes, directory, path, id, version]
    """
    with open(os.path.join(META_OUT, "pdfs.csv"), 'r') as file:
        csv_reader = csv.reader(file)
        metadata = list(csv_reader)

    # Sort metadata based on arxivid  s.t. one can use the same index across different machines
    metadata.sort(key=lambda x: x[3])

    # Print some stats
    log.info("The metadata has {} entries and their size is overall {} GB.".format(len(metadata),
                                                                                   sum(int(entry[0]) for entry in
                                                                                       metadata) / (
                                                                                       1e+9)))

    return metadata


def select_pdfs_to_download(start_index, max_size, downloaded_ids):
    """
    Selects pdfs to download based on a start index and a max size in gb that can be downloaded
    :param start_index: index from which the search starts
    :param max_size: max size in gb that should be stored
    :param downloaded_ids: list of ids of pdfs that are already downloaded (in the download directory)
    :return: a slice of the metadata of pdfs that can be downloaded like this
    """
    metadata = get_stored_metadata()
    sliced_metadata = metadata[start_index:]
    selected_pdfs = []
    max_size_in_bytes = max_size * 1e+9

    downloaded_ids_set = set(downloaded_ids)

    for entry in sliced_metadata:
        # Check that the size of the selected pdfs is smaller than max size
        max_size_in_bytes -= int(entry[0])
        if max_size_in_bytes < 0:
            end_index = metadata.index(entry)
            break
        # Check if entry is already downloaded and skip if that is the case
        if entry[3] in downloaded_ids_set:
            continue

        selected_pdfs.append(entry)
    else:
        # If the loop does finish normally e.g. no break is used, then the loop ended because run through all entries
        # Thus end index is the last index of the metadata list
        end_index = len(metadata) - 1

    return selected_pdfs, end_index


def store_pdf_list(pdf_metadata_to_download):
    """
    Store paths to pdf that shall be downloaded in a file s.t. gsutil can use the file for download
    However for pdfs from before 2007, a single filelist must be created. Thus, a file for each different directory type is created
    """
    if not os.path.exists(FILELISTS_OUT):
        os.makedirs(FILELISTS_OUT)

    # Remove existing file lists from a perhaps previous execution
    txtfiles = glob.glob('{}/*.*txt'.format(FILELISTS_OUT))
    for tf in txtfiles:
        os.remove(tf)

    # Split by top directory stored in bucket
    split_entries = {}
    for entry in pdf_metadata_to_download:
        dir = entry[1].split("/")[1]
        if dir not in split_entries:
            split_entries[dir] = []
        split_entries[dir].append(entry[2])

    # Save each file list
    for key, value in split_entries.items():
        filelist = [entry + "\n" for entry in value]
        # Remove linebreak of last entry to avoid empty line at end of file
        filelist[-1] = filelist[-1][:-1]  # only -1 as linebreak seems to count as one char

        with open(os.path.join(FILELISTS_OUT, "{}.txt".format(key)), "w+") as out:
            out.writelines(filelist)


def download_pdf(parallel):
    """
    Downloads PDFs from Google Bucket into one (final) directory
    :param parallel: Boolean stating whether or not parallel downloading should be used
    :return error_raised: if false no error, if true error occurred
    """
    # Get all files in filelist directory (adapted from https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory)
    filelists = [f for f in os.listdir(FILELISTS_OUT) if os.path.isfile(os.path.join(FILELISTS_OUT, f))]

    # Create tmp folder if is not existing
    tmp_out_folder = os.path.join(PDF_OUT, "tmp")
    if not os.path.exists(tmp_out_folder):
        os.makedirs(tmp_out_folder)

    error_raised = False
    for filelist in filelists:
        dir = filelist[:-4]

        try:
            # Build execution command
            ex_cmd = ["gsutil"]
            if parallel:
                ex_cmd.append("-m")
            ex_cmd += ["cp", "-I", "{}".format(tmp_out_folder)]
            pipe_cmd = ["cat", "{}".format(os.path.join(FILELISTS_OUT, filelist))]
            # Download/Execute commands (here due to usage of pipes) a bit more complicated see https://docs.python.org/2/library/subprocess.html#replacing-shell-pipeline
            log.info("Start Download of PDFs for directory {}".format(dir))
            p1 = subprocess.Popen(pipe_cmd, stdout=subprocess.PIPE)
            p2 = subprocess.Popen(ex_cmd, stdin=p1.stdout, stdout=subprocess.PIPE)
            p1.stdout.close()
            output = p2.communicate()[0]
        except Exception as e:
            log.exception("Fatal error in gsutil usage. Finish clean up and shut down")
            error_raised = True

        # Move renamed files to main folder
        log.info("Start moving PDF files for directory {}".format(dir))
        txtfiles = glob.glob('{}/*.pdf'.format(tmp_out_folder))
        for tf in txtfiles:
            if dir == "arxiv":
                shutil.move(tf, os.path.join(PDF_OUT, os.path.basename(tf)))
            else:
                shutil.move(tf, os.path.join(PDF_OUT, "{}_{}".format(dir, os.path.basename(tf))))

        if error_raised:
            break

    # Delete tmp folder
    log.info("Remove tmp folder")
    shutil.rmtree(tmp_out_folder)

    return error_raised

def downloaded_so_far():
    """
    Collects the ArxivIDs of all so far downloaded PDFs
    :return:
    """
    pdf_files = glob.glob('{}/*.pdf'.format(PDF_OUT))
    downloaded_ids = []
    # Get ids
    for pdf in pdf_files:
        filename = os.path.splitext(os.path.split(pdf)[1])[0]
        if "_" in filename:
            # Replace _ to / s.t. ID is correct arxiv id
            filename = filename.replace("_", "/")

        # Remove version
        filename = filename.rsplit("v", 1)[0]

        downloaded_ids.append(filename)

    return downloaded_ids
