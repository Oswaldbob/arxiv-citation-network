import log_config_util
from arxivcitationnetwork import ArxivCitationNetwork, format_name_to_id
from collections import defaultdict

log = log_config_util.get_logger("merger")
N = 5  # Number of status updates per loop


def merge_bierbaum_network(citation_network: ArxivCitationNetwork, metadata_aid_to_doi_title):
    """
    "Merge" Bierbaum Network by parsing it into a new object structure and cleaning it.
    In this code the network created by the work of Clement et al. is referenced
    as "bierbaum's network" simply because it was the root name of the repository.
    """
    bierbaum_network = log_config_util.load_metadata("merged_internal-citations.json")

    # Stats for loop counter

    entries, counter_mark = log_config_util.get_loop_stats(bierbaum_network, N)
    log.info("Start Parsing Bierbaum's network. Entries: {}".format(entries))
    for counter, content in enumerate(bierbaum_network.items()):
        log_config_util.update_counter(counter, counter_mark, entries, N, log)

        aid = content[0]
        arxiv_citations = content[1]

        # Stripping version number for now
        aid_without_version = log_config_util.remove_version_ending(aid)
        arxiv_citations_without_version = list(map(log_config_util.remove_version_ending, arxiv_citations))

        # Get metadata
        metadata = metadata_aid_to_doi_title.get(aid_without_version, [])
        if metadata:
            doi = metadata[0]
            title = metadata[1]
        else:
            doi = title = ""

        citation_network.add_arxiv_paper(aid_without_version, arxiv_citations_without_version, [], doi, title)

    # Clean data
    log.info("Clean ArXiv IDs")
    valid_arxiv_ids = set(metadata_aid_to_doi_title.keys())
    faulty_ids = citation_network.clean_arxiv_ids(valid_arxiv_ids)
    log.info("Cleaned {} bad Arxiv IDs".format(len(faulty_ids)))

    log.info("Finished Parsing Bierbaum's network")


def transform_arxiv_metadata(metadata_aid_to_doi_title):
    """
    Transform arxiv metadata into specific dicts of data that is contained in it overall for faster access
    Titles are already formatted accordingly!
    """

    # Get data structures for fast comparison
    doi_to_arxiv_id = defaultdict(list)
    title_to_arxiv_id = defaultdict(list)
    for arxiv_id, content in metadata_aid_to_doi_title.items():
        # Add doi if exists
        if content[0]:
            doi_mag = content[0].upper()  # make doi values upper case per definition of MAG
            doi_to_arxiv_id[doi_mag] = arxiv_id  # Ignoring possible duplicates here, match to "last" arxiv_id

        # Add title
        title = content[1]
        title_to_arxiv_id[format_name_to_id(title)] = arxiv_id  # Ignoring possible duplicates here

    return title_to_arxiv_id, doi_to_arxiv_id


def add_arxiv_id_to_mag_data(magid_to_data, metadata_aid_to_doi_title):
    """ Try to match arxiv metadata title to the titles of a MAG ID. For each match add the corresponding arxiv ID
        Afterwards all mag_ids are matched to an arxiv paper if they correspond to an arxiv paper
        Thus, all papers that are not matched are most likely not an arxiv paper and thus external
    """

    title_to_arxiv_id, doi_to_arxiv_id = transform_arxiv_metadata(metadata_aid_to_doi_title)
    valid_titles = set(title_to_arxiv_id.keys())
    valid_dois = set(doi_to_arxiv_id.keys())

    # Go through all entries and add arxiv ID if possible (roughly adds 200k IDs)
    entries, counter_mark = log_config_util.get_loop_stats(magid_to_data, N)
    log.info("Start Preprocessing MAG Data. Entries: {}".format(entries))
    for counter, content in enumerate(magid_to_data.items()):
        log_config_util.update_counter(counter, counter_mark, entries, N, log)

        data = content[1]

        # Check arxiv_id
        arxiv_id = data[3]
        if arxiv_id:
            continue

        # Check doi
        doi = data[0]
        if doi in valid_dois:
            data[3] = doi_to_arxiv_id[doi]
            continue

        # Check title (using simple title matching)
        paper_title_for_matching = ''.join(data[1].split()).lower()
        original_title_for_matching = ''.join(data[2].split()).lower()

        if original_title_for_matching in valid_titles:
            data[3] = title_to_arxiv_id[original_title_for_matching]
            continue

        if paper_title_for_matching in valid_titles:
            data[3] = title_to_arxiv_id[paper_title_for_matching]

    log.info("Finished Preprocessing MAG Data")


def get_mag_external_papers_stats(magid_to_data):
    """Get stats about external papers """
    external_papers = {mag_id: data for mag_id, data in magid_to_data.items() if not data[3]}

    # Get stats about title duplicates
    external_papers_title = set([data[2] for mag_id, data in external_papers.items()])
    log.info("Title Duplicates in external non-arxiv Papers: {} ({:.2%})".format(
        len(external_papers) - len(external_papers_title), 1 - len(external_papers_title) / len(external_papers)))


def add_external_papers_mag(citation_network: ArxivCitationNetwork, magid_to_data):
    """Add external papers to citation network based on MAG data"""

    entries, counter_mark = log_config_util.get_loop_stats(magid_to_data, N)
    log.info("Start adding external MAG papers. Entries: {}".format(entries))
    for counter, content in enumerate(magid_to_data.items()):
        log_config_util.update_counter(counter, counter_mark, entries, N, log)

        mag_id = content[0]
        data = content[1]

        # If it is an external paper (e.g. has no referenced arxiv ID) add it
        if not data[3]:
            title = data[2]  # Using original title not paper title of MAG
            doi = data[0]
            citation_network.add_external_paper(title, doi, mag_id)
    log.info("Finished adding external MAG papers")


def add_arxiv_papers_mag(citation_network: ArxivCitationNetwork, magid_to_data, aid_to_ref_magids,
                         metadata_aid_to_doi_title):
    """
        Add arxiv paper to citation network based on the mag data.
        We need to add internal arxiv papers based on MAG since the data so far is based on the
        successfully downloaded ones but the MAG results are based on the metadata.
    """

    # Find arxiv IDs that need to be added
    to_add_ids = set(aid_to_ref_magids.keys()) - set(citation_network.arxiv_papers.keys())
    log.info("Need to add {} Arxiv IDs that are in the MAG data but not in the network".format(len(to_add_ids)))

    entries, counter_mark = log_config_util.get_loop_stats(to_add_ids, 2)
    log.info("Start adding arxiv papers from MAG Data. Entries: {}".format(entries))
    for counter, arxiv_id in enumerate(to_add_ids):
        log_config_util.update_counter(counter, counter_mark, entries, 2, log)

        # Get metadata
        metadata = metadata_aid_to_doi_title.get(arxiv_id, [])
        if metadata:
            doi = metadata[0]
            title = metadata[1]
        else:
            doi = title = ""

        # Here, we do not add any citations since the next step of the pipeline will do this
        citation_network.add_arxiv_paper(arxiv_id, [], [], doi, title)

    log.info("Finished adding arxiv papers from MAG Data")


def add_citations_mag(citation_network: ArxivCitationNetwork, magid_to_data, aid_to_ref_magids):
    """Extend citation connections of network based on MAG data"""

    # Stats
    pre_ac = citation_network.number_arxiv_citations()
    pre_ec = citation_network.number_external_citations()
    number_overall_references_mag = 0
    for key, value in aid_to_ref_magids.items():
        number_overall_references_mag += len(value)

    entries, counter_mark = log_config_util.get_loop_stats(aid_to_ref_magids, N)
    log.info("Start extending citations by MAG Data. Entries: {}".format(entries))
    for counter, content in enumerate(aid_to_ref_magids.items()):
        log_config_util.update_counter(counter, counter_mark, entries, N, log)

        # Get content and object
        arxiv_id = content[0]
        ref_mag_ids = content[1]
        arxiv_paper_object = citation_network.arxiv_papers[arxiv_id]

        # Extend citations
        for ref_mag_id in ref_mag_ids:
            ref_data = magid_to_data[ref_mag_id]
            ref_arxiv_id = ref_data[3]
            ref_title = ref_data[2]

            # Arxiv Reference
            if ref_arxiv_id:
                arxiv_paper_object.add_arxiv_citation(ref_arxiv_id)
                continue

            # External Reference
            arxiv_paper_object.add_external_citation(ref_title)

        # Remove duplicates that might have been created by direct approach above (this improves performance)
        arxiv_paper_object.remove_duplicates_in_citations()

    log.info("Finished extending citations by MAG Data")

    # Stats
    post_ac = citation_network.number_arxiv_citations()
    new_ac = post_ac - pre_ac
    post_ec = citation_network.number_external_citations()
    new_ec = post_ec - pre_ec
    not_new = number_overall_references_mag - (new_ec + new_ac)
    prev_work = max(pre_ac - not_new, 0)
    log.info(("Before adding MAG Data, the Citation Network had {} arxiv and {} external citations. \n" +
              "Using the MAG Data, {} arxiv citations ({:.2%} of all MAG References)" +
              " and {} external citations ({:.2%} of all MAG References) were added" +
              " (Here one can read: citations = edges).\n" +
              "Consequently, {} ({:.2%}) of the MAG reference were already in the network by previous work or a caused by title duplicates. \n" +
              "Furthermore, the previous work was able to find {} citations not found by the MAG. \n" +
              "In other words, {:.2%} of the references generated by previous work were not found in the MAG.").format(
        pre_ac, pre_ec,
        new_ac, new_ac / number_overall_references_mag,
        new_ec, new_ec / number_overall_references_mag,

        not_new, not_new / number_overall_references_mag,

        prev_work, (
                prev_work / pre_ac) if pre_ac else 0))  # Avoid division by zero, idea from: https://stackoverflow.com/a/27317595


def merge_mag_data(citation_network: ArxivCitationNetwork, metadata_aid_to_doi_title):
    """Merge MAG Data into citation network"""

    # Load MAG Data
    aid_to_ref_magids = log_config_util.load_metadata("aid_to_ref_magids.json")
    magid_to_data = log_config_util.load_metadata("magid_to_data.json")

    # Preprocess magid_to_data
    add_arxiv_id_to_mag_data(magid_to_data, metadata_aid_to_doi_title)  # roughly adds 200k Arxiv IDs

    # Stats
    get_mag_external_papers_stats(magid_to_data)

    # Main Steps of Merging
    log.info("Start Merge of MAG Data")
    add_external_papers_mag(citation_network, magid_to_data)
    add_arxiv_papers_mag(citation_network, magid_to_data, aid_to_ref_magids, metadata_aid_to_doi_title)
    add_citations_mag(citation_network, magid_to_data, aid_to_ref_magids)
    log.info("Finished Merge of MAG Data")


def preprocessing_parser_data(parsed_aids_not_matched, metadata_aid_to_doi_title):
    """
    Preprocess parser data
     - remove duplicates, split into external/internal citations and remove bad arxiv IDs

    New format:
        {arxiv_id: ([arxiv_ids,...], [titles, ...]),...} whereby titles are external and arxiv_ids internal papers
    """

    # Get metadata data
    title_to_arxiv_id, _ = transform_arxiv_metadata(metadata_aid_to_doi_title)
    valid_titles = set(title_to_arxiv_id.keys())
    valid_arxiv_ids = set(metadata_aid_to_doi_title.keys())

    # Preprocessing - Get List of arxiv IDs without version and titles in correct format and
    log.info("Preprocessing parsed data")
    parser_data = {}
    for arxiv_id, content in parsed_aids_not_matched.items():
        # arxiv_id_no_version = log_config_util.remove_version_ending(arxiv_id)
        arxiv_id_no_version = log_config_util.arxiv_filename_to_id(log_config_util.remove_version_ending(arxiv_id))

        # Get list of referenced titles and eliminate possible duplicates
        cited_titles = set([format_name_to_id(ref["title"]) for ref in content])

        # Split for external/internal citations
        arxiv_citations = []
        external_citations = []
        for cited_title in cited_titles:
            if cited_title in valid_titles:
                arxiv_citations.append(title_to_arxiv_id[cited_title])
            else:
                external_citations.append(cited_title)

        # Duplicate arxiv IDs in the parsed set itself (i.e. version difference) will be eliminated by this
        # However, the parsed set should not contain multiple entries for different versions anyhow.
        parser_data[arxiv_id_no_version] = (arxiv_citations, external_citations)

    # Clean bad arxiv IDs
    invalid_entries = set(parser_data.keys()) - set(valid_arxiv_ids)
    for key in invalid_entries:
        parser_data.pop(key)

    # Print stats about external/internal citations
    pre_overall_ref = sum([len(content) for key, content in parsed_aids_not_matched.items()])
    post_overall_ref = sum([len(content[0]) + len(content[1]) for key, content in parser_data.items()])
    internal = sum([len(content[0]) for key, content in parser_data.items()])
    external = sum([len(content[1]) for key, content in parser_data.items()])
    log.info(("Overall references before preprocessing {}, afterwards {}. " +
              "Extracted overall internal (arxiv) references: {}; Extracted overall external references {}.").format(
        pre_overall_ref, post_overall_ref,
        internal, external)
    )

    return parser_data


def merge_parser_data(citation_network: ArxivCitationNetwork, metadata_aid_to_doi_title, input_parsed_data):
    """
        Add parser data to citation network
        As this is in general 'more' unsafe than previous methods, do cautious injection.
    """

    parser_data = preprocessing_parser_data(input_parsed_data, metadata_aid_to_doi_title)

    log.info("Start mering parsed data")

    # Add arxiv papers (Safely)
    existing_papers = set(citation_network.arxiv_papers.keys())
    for key, data in parser_data.items():
        if key in existing_papers:
            continue
        citation_network.add_arxiv_paper(key)

    # Find external papers
    external_papers = []
    for key, data in parser_data.items():
        external_papers += data[1]
    external_papers = set(external_papers)

    # Add external papers safely
    existing_external_papers = set(citation_network.external_papers.keys())
    to_add = external_papers - existing_external_papers
    for ex_paper_title in to_add:
        citation_network.add_external_paper(ex_paper_title, format_name=False)

    # Add citations safely
    for key, data in parser_data.items():

        # Get object
        arxiv_paper_obj = citation_network.arxiv_papers[key]

        # Get list of citations that still need to be added
        to_add_arxiv_cites = set(data[0]) - set(arxiv_paper_obj.arxiv_citations)
        to_add_external_cites = set(data[1]) - set(arxiv_paper_obj.external_citations)

        # Add citations
        for to_add_a_id in to_add_arxiv_cites:
            arxiv_paper_obj.add_arxiv_citation(to_add_a_id)

        for to_add_title in to_add_external_cites:
            arxiv_paper_obj.add_external_citation(to_add_title, format_title=False)

    log.info("Finished mering parsed data")
