# Overview
This document describes a script which is used to parse PDFs using Science Parse cli and extract information about references.

## Script
`parse_main.py` executes consequentially the following three steps:
1. [Optional] Copy PDFs to parse from source folder to target folder. (This step is performed due the limitations of Science Parse. Science Parse takes as an input argument path to a single file or to a directory. If a path to a directory is specified, all the PDFs in that directory will be parsed. This workaround was used when it was required to parse only a subset of files)
2. Parse PDFs using Science Parse. After this step there are as many JSONs containing different information as PDFs which were parsed.
3. Extract references. During this step, the references from all JSONs are extracted and put into one file.

Implementation of the described steps is contained in `parse_pdfs.py`.

## Install Science Parse
https://github.com/allenai/science-parse  
Download source code and build jar file using `sbt`  
Installation details and usage in CLI mode: https://github.com/allenai/science-parse/blob/master/cli/README.md

## Configuration and usage
`config.ini` should be created based on provided `example.config.ini`. This configuration file specifies the following paths:  

| Name | Description |
| ------------- | ------------- |
| science_parse_jar | science-parse-cli jar file |
| origin_pdfs | source folder from which PDFs could be copied (required for "copy" step) |
| aids_to_copy | arXiv ids of PDFs to copy (required for "copy" step) |
| pdfs_to_parse | folder with PDFs to parse |
| parsing_results | folder where to save parsing results (JSON files for all PDFs) |
| extracted_references | final output |

In order to execute the script, run the following command:
```
python parse_main.py
```

## Output
Extracted reference information is stored as a JSON file in the shape of dict, where key is an Arxiv ID:
```json
{
    "0704.2282v2":
    [
        {
            "author": ["F.L. Carter"],
            "title": "Molecular Electronic Devices"
        },
        {
            "author": ["C.A. Coulson"],
            "title": "Valence"
            }
        ]
}
```


# Parsing statistics
## Papers not matched by MAG
There are 69645 papers which were not matched by MAG. 1% (766) of these papers are not downloaded (`aids_not_matched.json` is based on the metadata while the downloader works on the data in the bucket).  
Arxiv IDs of papers which were not matched and were not downloaded are not included in the final file `parsed_aids_not_matched.json`.
* **Results on cssh2**: 13558 PDFs, parsed 13558 (100%)
* **Results on cssh7**: 55321 PDFs, parsed 55303 (99.96%)


## Sampled 100k papers
100000 papers were sampled randomly from all downloaded and successfully converted PDFs (corresponding Arxiv IDs are in `sampled_aids_100.json`).
* **Results on cssh2**: 55989, parsed: 55981 (99.98%), time: 97 minutes
* **Results on cssh7**: 44011, parsed: 44005 (99.98%), time: 77 minutes

## Papers without references in MAG
There are 387154 Arxiv papers in MAG which have no references. 0.8% (3112) of these papers are not downloaded.
* **Results on cssh2**: 184909, parsed 184886 (99.99%)
* **Results on cssh7**: 199133, parsed 199071 (99.97%)

Extracted from 383956 (99.17%); References-Overall: 7239735; References-Unique: 2582331 (Unique: 35.67%).
