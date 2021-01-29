# Extending the ArXiv Citation Network

This repository corresponds to the code of a project related to a practical at the RWTH University, Aachen Germany.  
The result, a citation network focused on arXiv, is available as a release. Additionally, the report about this project
is provided as part of the repository (PDF).

The work is build upon previous work by Clement et al. (see: https://github.com/mattbierbaum/arxiv-public-datasets). It
is not a fully fetched library or a tool but rather potentially reusable code to achieve our or similar goals.

In particular, this work contains a new script to download all PDFs from arXiv's public Google Cloud Storage
bucket (https://console.cloud.google.com/storage/browser/arxiv-dataset), convert them to text files and extract an
internal regex-based arXiv citation network by reusing work from Clement et al. Furthermore, a parser called Science
Parse was used to extract new citations. Additionally, a newly created Microsoft Academic Graph Extractor (MAGE), which
extracts citations of arXiv papers from the Microsoft Academic Graph (
MAG) (https://www.microsoft.com/en-us/research/project/microsoft-academic-graph/), were utilized.  
More details can be found in the report or corresponding subdirectories.

## Abstract

Citation networks are used to trace citations between publications. They enable analysis of the impact of specific
publications or the calculation of bibliographic metrics. Our project focused on extending an internal citation network
created by Clement et al., which was built upon the open-access scholarly publication archive arXiv.org. We extend their
result in three ways: 1) Adding references from new publications using previous work by Clement et al.; 2) Extracting
references of an arXiv publication from the Microsoft Academic Graph; 3) Mining arXiv PDFs for references using Science
Parse. The new methods 2. and 3. enabled us to extend the citation network with citations of external—not on
arXiv—publications. As a result, we were able to expand the initial internal citation network with 1.79 million nodes
and 10 million edges to a citation network with 7.36 million nodes and 48.8 million edges which also captures outgoing
citations. In particular, the number of internal edges was also increased from 10 million to 23.9 million.

## Content Overview

- 'data_acq': contains code to download the PDF, convert them to fulltext and create the intra-citation network
- 'parse_references' contains code to parse reference list from the given PDF to JSON using open-source parsers
- 'mag' contains code for the Microsoft Academic Graph Extractor
- 'analysis' contains code for analysing our data results
- 'important_data' contains short descriptions of the resulting data