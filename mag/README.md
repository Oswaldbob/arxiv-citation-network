# Overview
Tools to extract references from the MAG that correspond to references of specific arxiv papers 
* MAG data schema: https://docs.microsoft.com/en-us/academic-services/graph/reference-data-schema

# Usage
* After editing example.config.ini files one needs to rename them to config.ini 

## Preprocessing (./preprocessing)
Extract required information for matching arxiv papers to mag papers from arxiv metadata

- Download the arxiv-metadata-oai-snapshot.json from here https://www.kaggle.com/Cornell-University/arxiv. Unzip it and put it into the META_OUT directory used in the config file. Thus, change the example config s.t. META_OUT is a directory in which the .json from above is stored and in which a new .json.gz (60+ MB) can be stored.  
- Execute the script pre_main.py
- Here: Metadata from update 18 was used. Downloaded from here: https://www.kaggle.com/Cornell-University/arxiv.

## Reference extractor (./ref_extractor)
Uses DOI, Title and URLs stored in MAG to match arxiv ID to references 

- Get access to MAG and edit the config file s.t. "meta" equals a path to some directory that can store metadata and that contains the .json output file of the preprocessing step and which can store all output files (1.5+ GB) ; "mag_base" equals the path to the MAG data directory in which Papers.txt and other MAG .txt files are stored (if for some reason a .txt file is not stored in this base directory, one needs to edit the code statements that open these files in mage.py)  
- Execute the script mag_main.py


# Data Problems

## Arxiv Metadata

Two version of the metadata exists. One hosted on kaggle (API Download only via authentication) and one hosted on the
bucket (free download as always). However the one on the bucket is a lot bigger yet worse (see below).

- Kaggle metadata: 2.7 GB, Entries: 1796907, DOI-Empty-% 0.48148179065471947 (updates weekly*)
- Bucket Metadata: 4.2 GB, Entries: 1687263, DOI-Empty-% 0.4745152356212398 (last update Aug 19, 2020)

As the Kaggle download is just a one time process (at the day we started the processing), automating it seem to be to
much right now as it requires additional authentication accounts, strange API usage or an additional download tool.

* As of now (2020-12-09) this is a false statement as for some reason the metadata is not updated weekly but was last
  update 17 days ago. Which is a first in the history of this dataset on kaggle.

The GCS bucket also hosts a version of the metadata. However, this version seems to be only existing for test purposes.
It is different from the version on Kaggle because it is bigger ($\sim$4.2 GB) but has less entries ($\sim$1.6 million).
This is unfortunate as an automated download of the metadata from Kaggle via its API requires account-based
authentication while the metadata on the bucket can be download like the PDFs without an account and without further
knowledge using a tool provided by GCS. Therefore, providing the metadata on the bucket would be advantageous for the
user.

## Arxiv Overall

As it seem, some papers (ca. 3000) are uploaded at least twice to ArXiv (assuming all titles are unique). See for
example: https://arxiv.org/abs/0704.0516, https://arxiv.org/abs/quant-ph/0012088. This problem also persistent in the
data that was downloaded (i.e. PDFS, Fulltext, Internal citation network) since these duplicates have different IDs and
are therefore treated as individual papers. Thus, this creates some problems for title comparison which need fixing.
However, this is not a big problem overall. If one would want to eliminate these duplicates from the final graph, it
would only require to match these duplicates again. Yet, as these are treated as individual papers by the graph, no
conflict arise for our processing.

## MAG Data

### Duplicates

The MAG Data for papers consist of a lot of duplicates. These are papers that have the same name and were simply
republished. This creates useless additional computation. This is also a problem if the references of such duplicates
are not properly connected. For now we are assuming that this is the case - else one would to filter the data and check
which of the possible same titled entries has the most references.

Example data: One MAG entry is for the publication with arxiv in 2019, the other for a conference in 2016 - same title
and possibly the same "actual" paper

    ['2953327271', '21298', '', 'Repository', 'the adaptive priority queue with elimination and combining', 'The Adaptive Priority Queue with Elimination and Combining', '', '2014', '2014-08-05', '2014-08-05', '', '2595101014', '', '', '', '', '', '', '6', '0', '0', 'arXiv: Distributed, Parallel, and Cluster Computing', '14558443', '20018', '2019-06-27\n']

    ['14558443', '20345', '10.1007/978-3-662-45174-8_28', 'Conference', 'the adaptive priority queue with elimination and combining', 'The Adaptive Priority Queue with Elimination and Combining', 'DISC', '2014', '2014-10-12', '', 'Springer, Berlin, Heidelberg', '', '1131603458', '4038532', '', '', '406', '420', '11', '10', '10', 'international symposium on distributed computing', '14558443', '20018', '2016-06-24\n']

# Results Example (not final results of our report)

## Summary 
Here safe means that all results are matched correctly. Unsafe means that it is to some degree based on chance. The result data can be found on cssh5 /home/lpurucker/mag/. For this, the ArXiv metadata from the 2020-11-22 was used. 

Start Data:  #Arxiv IDs: 1796907. #DOIs 929943 (51.75%). #Unqiue Titles 1793433 (99.81%). 

* Was able to match **95.52%** (1716471) of all Arxiv IDs to MAG IDs using DOI, URLs and title matching. All these matches were created in a safe fashion. 
* For **77.93%** (1400344) arxiv Papers at least one reference could be found. These 77.93% arxiv Papers reference (with duplicates) 39057792 papers. Each paper references on average 27.89 papers. All of these references correspond to 5427271 unique papers (duplicate-%: 86.10%).
* For **98.34%** (5336910) referenced Papers data could be found in the MAG. To 20.85% (1112887) of the data an arxiv ID was matchable (i.e. these referenced papers are known to be arxiv papers). However, for all other referenced papers (90361) no data could be found in the MAG even so the references were extracted from the MAG.  
* Time taken overall: ca. 50+ minutes
* Output: 
    - Arxiv IDs associated to referenced MAG IDs "aid_to_ref_magids.json" (555 MB) 
    - MAG IDs associated to data of this paper (DOI if exists, paper_title, original_title, arxiv_id if known) "magid_to_data.json" (1 GB)

## Run
2020-12-18 10:31:20,280 - main - INFO: Get IDs \
2020-12-18 10:31:29,247 - MAGE - INFO: #Arxiv IDs: 1796907. #DOIs 929943 (51.75%). #Unqiue Titles 1793433 (99.81%). 

2020-12-18 10:41:42,112 - MAGE - INFO: For 28140 DOIs no match was found (3.03%). Matched for 901803 DOIs \
2020-12-18 10:41:42,112 - MAGE - INFO: Overall matched arxiv papers to MAG papers is now: 901803. [Matched 50.19% of all Arxiv IDs so far] \
2020-12-18 10:41:42,676 - MAGE - INFO: Start searching for ArxivIDs matches in PaperUrls.txt [Be patient it has a lot of lines] 

2020-12-18 10:45:40,187 - MAGE - INFO: Using URLs it was possible to find new MAG ID matches for 479994 Arxiv Papers \
2020-12-18 10:45:40,187 - MAGE - INFO: Overall matched arxiv papers to MAG papers is now: 1381797. [Matched 76.90% of all Arxiv IDs so far] \
2020-12-18 10:45:42,824 - MAGE - INFO: Start searching for Title matches in Papers.txt for 414562 titles of 415110 Arxiv IDs (Duplicate titles: 0.13%). 

2020-12-18 11:00:57,521 - MAGE - INFO: Was trying to match 414562 titles. Was able to match 334473 titles (80.68%). \
2020-12-18 11:00:57,521 - MAGE - INFO: Based on these titles. Was trying to match 415110 arxiv IDs. Was able to match 334674 arxiv IDs (80.73%). \
2020-12-18 11:00:57,521 - MAGE - INFO: Overall matched arxiv papers to MAG papers is now: 1716471. [Matched 95.52% of all Arxiv IDs so far] 

2020-12-18 11:09:24,879 - MAGE - INFO: Original unique MAG entries that are cited: 1712390. For 396563 arxiv Papers matched to these MAG IDs no references could be found (22.07%). For 4081 of these a MAG match was found but no references of this match. Overall References (with duplicates): 39057792. Ref-Avg. for arxiv paper: 27.8915695000657 \
2020-12-18 11:09:34,164 - MAGE - INFO: Found 5427271 unique references by arxiv papers in MAG. Duplicate-%: 86.10% 

2020-12-18 11:19:49,595 - MAGE - INFO: Found data for 5336910 referenced MAG IDs (98.34%). To 1112887 of these MAG IDs an arxiv ID was matched (20.85%). Unable to match 90361 MAG IDs to MAG data. \
2020-12-18 11:19:49,595 - MAGE - INFO: Start saving /home/lpurucker/mag/magid_to_data.json \
2020-12-18 11:20:19,163 - MAGE - INFO: Start saving /home/lpurucker/mag/aid_to_ref_magids.json \
2020-12-18 11:20:41,027 - main - INFO: Finished MAG Processing 

## Problems

* Unmatched Arxiv papers: A time difference in the download of metadata and MAG might be the reason. In other words, the
  arxiv metadata is newer than the MAG download and thus has more entries which are not yet captured by MAG.
* Remark: with the newest version of Papers.txt found data for referenced MAG IDs correspond to 100% - these results are
  however not captured here

# FAQ
* Automate Download from kaggle? No, manual should be good enough for now. 
