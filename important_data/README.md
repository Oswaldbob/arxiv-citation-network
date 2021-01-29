See the release for our final results the `citation_network.json`. The other intermediate results can be shared, if
needed, through us directly. To obtain MAG data, please contact the responsible people at
Microsoft (https://www.microsoft.com/en-us/research/project/microsoft-academic-graph/).

# Description of Created Data

* `merged_internal-citations.json` - Merged output of Bierbaum's original work on our downloaded dataset. This is an
  internal-citation network of the form: {"arxiv_id": [referenced_arxiv_id,...],...}
  * Problems:
    - Some arxiv IDs still contain their version number
    - This is based on REGEX and thus has some specific problem and is missing entries, for example, some papers have a
      self references due to version numbers
  * Other:
    - The keys of this corresponds to a list of the Arxiv IDs of all PDF that were downloaded and successfully converted
      into PDF
  * From: data_acq
* `pdf.csv` - Extracted metadata from the Google Cloud Bucket via Gsutil
  * Each line represents a paper that can be downloaded with the format: size in bytes, directory, path, id, version
  * From: data_acq
* `arxiv_id_to_doi_title.json` - Arxiv IDs matched to doi (if exists) and title from arxiv metadata
  * Dict in shape of {"arxiv_id": [doi or null, Title],...}
  * From: mag -> preprocessing
* `aid_to_ref_magids.json` - Arxiv IDs matched to a list of MAG IDs corresponding to referenced papers (mag ->
  ref_extractor)
  * Dict in shape of {"arxiv_id": [MAG ID,...],...}
  * From: mag -> ref_extractor
* `magid_to_data.json` - MAG IDs matched to a list of data corresponding to data of the papers
  * Collect DOI (if exists), titles and arxiv id (if known) for all papers that were referenced by an arxiv paper
  * Dict in shape of {"mag_id": [doi or empty, paper_title, original_title, arxiv_id or empty],...}
  * From: mag -> ref_extractor
* `aids_not_matched.json` - List of arxiv IDs that were not matched to a MAG ID using the MAG Data
  * List in shape of ["arxiv_id",...]
  * From: mag -> ref_extractor
* `aids_without_ref.json` - List of Arxiv IDs that are matched to a MAG ID but for which no reference was found
  * List in shape of ["arxiv_id",...]
  * From: mag -> ref_extractor
  * Due to a bug in the MAGE, aids_without_ref.json currently also includes the IDs that were not matched. (Fixable by
    executing the MAGE again). The "bug" version is kept here, as this is used for our final results and does not
    meaningfully change anything.
* `sampled_aids_100k.json` - List of 100000 randomly sampled Names (Arxiv IDs) of all downloaded and successfully
  converted PDFs which are used for our analysis
  * Note: Arxiv IDs contain version number just like the downloaded .txt/.pdf files however in the .txt or .pdf files "
    /" is replaced with "_" if existing in the Arxiv ID.
  * From: analysis
* `citation_network.json` - Final output of merging all our data together into one citation network
  * From: network_builder
  * Shape: {"arxiv_papers": {arxiv_id: ([arxiv ids of internal citations],[titles of external citations]),... },
    "external_papers": [title,...]}
* `parsed_aids_not_matched.json` - Arxiv IDs matched to a list of corresponding references for Arxiv papers which were not matched to a MAG ID using the MAG Data
  * Dict in shape of {"arxiv_id":[{"author", "title"},...],...}
  * From: parse_references
  * Remark: Arxiv IDs contain version number and "_" instead of "/" as it is coming from the download
* `parsed_sampled_100k.json` - Arxiv IDs matched to a list of corresponding references for 100000 Arxiv papers which were randomly sampled
  * Dict in shape of {"arxiv_id":[{"author", "title"},...],...}
  * From: parse_references
  * Remark: Arxiv IDs contain version number and "_" instead of "/" as it is coming from the download
* `parsed_aids_without_ref.json` - Arxiv IDs matched to a list of corresponding references for Arxiv papers which do not have references in MAG
  * Dict in shape of {"arxiv_id":[{"author", "title"},...],...}
  * From: parse_references
  * Remark: Arxiv IDs contain version number and "_" instead of "/" as it is coming from the download

