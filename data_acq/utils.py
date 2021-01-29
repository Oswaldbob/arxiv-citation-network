import subprocess
import re


def get_all_base_dir():
    """
    Get all base directories of pdfs
    :return: list of strings corresponding to relative path to dir starting from the bucket root
    """
    result = subprocess.run(["gsutil", "ls", "gs://arxiv-dataset/arxiv/"],
                            capture_output=True, text=True)
    result.check_returncode()  # If returncode is non-zero, raise a CalledProcessError.
    lines = result.stdout.split("\n")

    # Hard coded exclude that it is not a file (by checking if it has a dot in its last part of the path
    relative_dir_paths = ["arxiv/" + tmp[4] + "/pdf" for line in lines if
                          (tmp := line.split("/")) and line and ("." not in tmp[-1])]

    return relative_dir_paths
