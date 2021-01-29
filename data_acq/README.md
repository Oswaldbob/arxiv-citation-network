# Overview

## Other

- Previous work: https://github.com/mattbierbaum/arxiv-public-datasets
- The data bucket: https://console.cloud.google.com/storage/browser/arxiv-dataset

## Data Stats

When last checked (2020-12-1), 1791489 articles where found in the bucket. The overall size of these were when
considering only the latest version: 1820.093762805 GB. To query this metadata information using gsutil it took ca. 30
minutes. This step does not need to be done multiple times if one can get the metadata file from someone that already
created it with this code.

As of now, the bucket is not update frequently anymore nor the metadata. However, this makes the metadata from update 18
and our downloaded data in sync again as they both were not updated anymore.

# The Tool

## Data acquisition Setup (only for Linux)

Install Python:

    sudo apt install python3 python3-pip python3-virtualenv poppler-utils

Download our code: (currently only manual or via gitlab later).

Setup python environment (at least 3.7): Create a python virtualenv called "arxiv". Only do the first part once and
activate it with the second part as needed anytime you want to run the code.

    virtualenv arxiv_venv (might need: --python=python3)
    . ~/arxiv_venv/bin/activate

Install python requirements (on some system, it is required to do pip instead of pip3, test this by using pip -V and check if it points to python 2 or python3)

    pip3 install -r requirements.txt

Install Google Cloud Downloader: Follow the guide here https://cloud.google.com/storage/docs/gsutil_install. However, there is no need to do "gcloud init", because there is no need to login.  (use the "linux" installation section if you have no sudo rights)

Change config: Rename /data_acq/example.config.ini to config.ini. Then, fill out open fields with absolute paths to directories. 

Additionally, one needs to have "pdftotext" installed on linux (most distribution have it installed by default).

### Info about variables
Currently, no CLI argument parser is implemented. Thus, changing them requires changing them in the main.py. Here are
short introductions to the variables:

    re_collect_metadata = False # If true, bucket will be quried for metadata and donwloaded - this might only need to be done once every month or so
    download = False # Preprocessing for and download of PDFs
    convert = False # Convert PDFs to 
    build_intra_cites = True # Create the intra-citation network data (json.gz)
    
    parallel_download = True # Allow parallel download for th gsutil tool
    start_index = 0 # Start index to search for PDFs to download. Usable s.t. different machines start at differend indizies. Starting indizie for another machine is given as output of the execution of the first machine. 
    pdf_max_size = 0.1 # Max sie in GB to Download PDFs 
    number_of_processes = 1 # set number of process for conversion and intra citation network creation, can be left away (None) such that the tool finds the appropiate (i.e. all) number of processes

An example for start_index/pdf_max_size: Lets say the first machine can store 100GB, then its start_index would be 0 and
pdf_max_size 100. Resulting from the execution (after determining the files to download) a message will be printed out
that mentions the next index the tool would need to start from to search pdfs such that no duplicates are downloaded on
the next machine.

## Output

During the execution, besides info messages, some python warnings from the gsutil tool may pop up.

The data_acq main.py will create in the meta_out path, 1 csv of metadata about the whole dataset (Size: ca.
170MB) [Needed for Downloading]. Furthermore, a directory named "filelists" and .txt files in this directory are
created [Needed for Downloading]. These correspond to lists of pdfs that will be downloaded (Size: variable but small).
Lastly, a "internal-citations.json.gz" file is created storing the intra-citation network [If selected]. The pdf_out
directory will be filled with all downloaded pdfs. The fulltext_out directory will contain all converted .txt files.

### In detail

The final output of the script corresponds to a .csv file of the information from step 1 ($\sim$170 MB) which is used
for downloading. Additionally, a set of files called "filelists" is created which correspond to the subset of PDFs that
were selected to be downloaded. All selected PDFs and all converted text files are stored in two separate output
directories. Finally, the script also creates the gzip-compressed JSON of the internal citation network. The overall
sizes of the script's output, i.e. the PDFs, text files and internal citation network, varies depending on the selected
subset. One can use the results below to approximate the size of a corresponding subset. The script can be executed on
multiple machines in parallel. Based on the selected subset of PDFs that shall be downloaded, the script initially
outputs the starting index for an additional machine. The final result, the internal citation network, can be merged by
concatenating all JSON file outputs of each machine. Similar, it supports multiprocessing in all but the first step.
Moreover, it is built to be idempotent. In other words, re-executions results in the same output. Additionally, the
script wont re-download/re-convert PDFs if they are already downloaded/converted to improve performance.

