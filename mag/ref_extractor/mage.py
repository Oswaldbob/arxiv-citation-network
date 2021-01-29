import log_config_util
import os
import json
from collections import defaultdict
from urllib.parse import urlparse

log = log_config_util.get_logger("MAGE")
MAG_BASE = log_config_util.get_mag_base()
META = log_config_util.get_meta()


class MAGE:
    """Microsoft Academic Graph Extractor class used to increase performance and usability"""

    def __init__(self, id_doi_title_dict, stats=True, title_matching_cutoff=0.95):
        self.stats = stats
        self.title_matching_cutoff = title_matching_cutoff

        # Sets used for lookup (one loop for all could be faster however this is comprehension)
        self.aid_set = set([key for key in id_doi_title_dict.keys()])
        self.number_aids = len(self.aid_set)
        self.doi_set = set([value[0].upper() for key, value in id_doi_title_dict.items() if
                            value[0]])  # To upper due to MAG definition of DOIs
        self.title_set = set([value[1] for key, value in id_doi_title_dict.items()])

        # Match dicts used to match parsed result to an arxiv id
        doi_to_aids = defaultdict(list)
        title_to_aids = defaultdict(list)
        for arxiv_id, content in id_doi_title_dict.items():
            if content[0]:  # skip if no doi exists
                # make doi values upper case per definition of MAG
                doi_mag = content[0].upper()
                # create dict where doi maps to arxiv aid
                doi_to_aids[doi_mag].append(arxiv_id)

            # dict where title maps to arxiv id
            title_to_aids[content[1]].append(arxiv_id)
        self.doi_to_aids = doi_to_aids  # Struct: {"doi": [arixv_id,...],...}  list of aids just in case it is possible that multiple exist
        self.title_to_aids = title_to_aids  # Struct: {"title": [arixv_id,...],...}  due to duplicates
        self.aid_to_title = {aid: value[1] for aid, value in id_doi_title_dict.items()}

        # Important data created by this class
        self.aid_to_magid = {}  # "arixv_id": "mag_id",...} | Connects arxiv_ids to MAG IDs
        self.aid_to_ref_magids = {}  # "arixv_id":["mag_id",...],...} | Connects arxiv_ids to reference IDs (which are MAG IDs)
        self.unique_ref_magids = []  # ["mag_id",...] | Set of all unique mag ids referenced by an arxiv paper
        self.magid_to_data = {}  # {"mag_id": [doi or empty, title, arxiv_id or empty],...} | Used to match references to elements of citation graph in the next processing step
        self.magid_to_aid = {}  # This is required as multiple magid can point to the same aid and this needs to be captured
        self.matched_aids_without_ref = []  # Used later to find all aids which are matched but have no reference
        # Print some stats
        if stats:
            log.info("#Arxiv IDs: {}. #DOIs {} ({:.2%}). #Unique Titles {} ({:.2%}).".format(
                len(self.aid_set), len(self.doi_set), len(self.doi_set) / len(self.aid_set),
                len(self.title_set), float(len(self.title_set) / len(self.aid_set))
            ))

    def match_doi(self):
        """Get MAG IDs based on DOI"""
        # Parse line by line
        log.info("Start searching for DOI matches in Papers.txt [Be patient it has 102800000+ lines]")
        with open(os.path.join(MAG_BASE, "Papers.txt")) as f:
            for counter, line in enumerate(f):
                # Only update count after 10.000.000 entries
                if counter % 10000000 == 0:
                    log.info("Processed {} lines so far".format(counter))

                # Get content
                content = line.split("\t")
                mag_id = content[0]
                doi = content[2]

                # Match papers and put into storage
                if doi in self.doi_set:
                    # Match doi to aids
                    arxiv_ids = self.doi_to_aids[doi]
                    # Save mag_id
                    for arxiv_id in arxiv_ids:
                        self.aid_to_magid[arxiv_id] = mag_id
                        self.magid_to_aid[mag_id] = arxiv_id
                    continue

        if self.stats:
            # Get number of DOIs for which no match was found
            nr_not_used_dois = len(self.doi_set) - len(self.aid_to_magid)
            log.info("For {} DOIs no match was found ({:.2%}). Matched for {} DOIs".format(
                nr_not_used_dois, nr_not_used_dois / len(self.doi_set), len(self.aid_to_magid)))
            self.log_matching_stats()

    def match_url(self):
        """Find MAG IDs for arxiv IDs in URLs of possible URLs"""

        pre_length = len(self.aid_to_magid)
        aids_not_matched = set(self.aids_not_matched())

        # Find URLs for arxiv IDs
        log.info("Start searching for ArxivIDs matches in PaperUrls.txt [Be patient it has a lot of lines]")
        with open(os.path.join(MAG_BASE, "PaperUrls.txt")) as f:
            for counter, line in enumerate(f):
                if counter % 100000000 == 0:
                    log.info("Processed {} lines so far".format(counter))

                # Get content
                content = line.split("\t")
                mag_id = content[0]

                url = content[2]
                if "arxiv" in url:
                    parsed_url = urlparse(url)

                    # Get arxiv id
                    base = os.path.basename(parsed_url.path)
                    base_without_ext = os.path.splitext(base)[0]
                    arxiv_id = base_without_ext.rsplit("v", 1)[0]

                    # Define arxiv ID if it is not a new arxiv id
                    if not ("." in arxiv_id):
                        # Get directory name
                        split_path = parsed_url.path.split("/")
                        # Skip if path is not long enough to include directory name (buggy entry)
                        if len(split_path) < 2:
                            # This is needed because PaperUrls.txt has 1 entry that just has as url "arxiv.org"...
                            continue
                        category_name = split_path[-2]
                        arxiv_id = category_name + "/" + arxiv_id

                    # Skip if not in to-match list
                    if arxiv_id in aids_not_matched:
                        # Save matching
                        self.aid_to_magid[arxiv_id] = mag_id
                        aids_not_matched.discard(arxiv_id)

                    # add to magid to aid because this is a valid entry of magids
                    if arxiv_id in self.aid_set:
                        # if check to verify that it is a real aid (this might also help to find duplicates from which not have a DOI)
                        self.magid_to_aid[mag_id] = arxiv_id

        if self.stats:
            added_aids = len(self.aid_to_magid) - pre_length
            log.info("Using URLs it was possible to find new MAG ID matches for {} Arxiv Papers".format(added_aids))
            self.log_matching_stats()

    def simple_match_title(self):
        """Match titles on the most basic technique of all"""

        # Get sets for look up
        aids_not_matched = set(self.aids_not_matched())
        pre_length_a = len(aids_not_matched)
        mids_matched = set(self.mids_matched())

        # Create a set of titles in lower case without whitespaces for matching
        arxiv_titles_to_match = set([''.join(title.split()).lower() for aid in aids_not_matched
                                     if (title := self.aid_to_title[aid])])
        pre_length = len(arxiv_titles_to_match)
        adapted_title_to_aids = {(''.join(key.split()).lower()): value for key, value in self.title_to_aids.items()}

        # Parse line by line
        log.info(("Start searching for Title matches in Papers.txt for {} titles of {} Arxiv IDs (Duplicate titles:" +
                  " {:.2%}). [Be patient it has 102800000+ lines]").format(
            pre_length, pre_length_a, (pre_length_a - pre_length) / pre_length_a))

        # Since one title can point to multiple arxiv IDs (due to duplicates) count actual number
        arxiv_ids_matched = 0

        with open(os.path.join(MAG_BASE, "Papers.txt")) as f:
            for counter, line in enumerate(f):
                # Only update count after 10.000.000 entries
                if counter % 10000000 == 0:
                    log.info("Processed {} lines so far".format(counter))

                # Get content
                content = line.split("\t")
                mag_id = content[0]

                # Skip if this mid is already matched (hence it does not need any further matching)
                # len < 5 check is needed as !one! entry of the dataset is wrong and does not have all fields
                if mag_id in mids_matched or (len(content) < 5):
                    continue

                # Get relevant content
                paper_title = content[4]
                original_title = content[5]

                paper_title_for_matching = ''.join(paper_title.split()).lower()
                original_title_for_matching = ''.join(original_title.split()).lower()

                if paper_title_for_matching in arxiv_titles_to_match:
                    # Match title to aids
                    arxiv_ids = adapted_title_to_aids[paper_title_for_matching]
                    # Save mag_id for all matched aids
                    for arxiv_id in arxiv_ids:

                        # Create link between mag_id and arxiv id
                        self.magid_to_aid[mag_id] = arxiv_id

                        if arxiv_id in aids_not_matched:
                            # Filter if for a name already a match was found
                            self.aid_to_magid[arxiv_id] = mag_id
                            arxiv_ids_matched += 1

                    # Removed matched title
                    arxiv_titles_to_match.discard(paper_title_for_matching)
                    continue

                # Required as distinct if case since this case means that the title is different in the arxiv dataset
                if original_title_for_matching in arxiv_titles_to_match:
                    arxiv_ids = adapted_title_to_aids[original_title_for_matching]
                    for arxiv_id in arxiv_ids:
                        self.magid_to_aid[mag_id] = arxiv_id
                        if arxiv_id in aids_not_matched:
                            self.aid_to_magid[arxiv_id] = mag_id
                            arxiv_ids_matched += 1
                    arxiv_titles_to_match.discard(original_title_for_matching)

        if self.stats:
            log.info("Was trying to match {} titles. Was able to match {} titles ({:.2%}).".format(
                pre_length, pre_length - len(arxiv_titles_to_match),
                            (pre_length - len(arxiv_titles_to_match)) / pre_length, ))
            log.info(
                "Based on these titles. Was trying to match {} arxiv IDs. Was able to match {} arxiv IDs ({:.2%}).".format(
                    pre_length_a, arxiv_ids_matched, arxiv_ids_matched / pre_length, ))
            self.log_matching_stats()

    def get_not_matched(self):
        """ Get a list of Arxiv IDs that are not matched"""

        matched_aids = set(self.aid_to_magid.keys())
        # Get a list of all aids that are not in matched_aids
        not_matched = [aid for aid in self.aid_set if not (aid in matched_aids)]

        return not_matched

    def log_matching_stats(self):
        log.info(
            "Overall matched arxiv papers to MAG papers is now: {}. [Matched {:.2%} of all Arxiv IDs so far]".format(
                len(self.aid_to_magid), len(self.aid_to_magid) / self.number_aids))

    def aids_not_matched(self):
        """Return Arxiv IDs which are so far not matched to a MAG ID"""
        matched_aids = set(list(self.aid_to_magid.keys()))
        aids_still_to_match = [aid for aid in self.aid_set if not (aid in matched_aids)]
        return aids_still_to_match

    def mids_matched(self):
        """Return MAG IDs which are so far matched to some Arxiv ID"""
        return [key for key in self.magid_to_aid.keys()]

    def get_reference_ids(self):
        """
        Go through the PaperReferences.txt from MAG and get all IDs of papers referenced by an id of an arxiv paper
        """
        # Sets used to find elements
        matched_mid_set = set([value for key, value in self.aid_to_magid.items()])
        cited_mid_to_aid = {mid: aid for aid, mid in self.aid_to_magid.items()}
        tmp_aid_to_refid = {aid: [] for aid in self.aid_set}

        # Parse line by line
        log.info("Start searching for references in PaperReferences.txt [This may take a while]")
        with open(os.path.join(MAG_BASE, "PaperReferences.txt")) as f:
            for counter, line in enumerate(f):
                # Only update count after 100.000.000 entries
                if counter % 100000000 == 0:
                    log.info("Processed {} lines so far".format(counter))

                # Get content
                content = line.rstrip().split("\t")
                mid = content[0]
                referenced_id = content[1]

                # Match ids and store reference
                if mid in matched_mid_set:
                    # Get arxiv id
                    arxiv_id = cited_mid_to_aid[mid]
                    # Append to list
                    tmp_aid_to_refid[arxiv_id].append(referenced_id)

        # Get some stats and remove empty entries
        empty = 0
        nr_ref = 0
        non_empty_aid_to_refid = {}
        empty_aid_to_refid = []
        matched_aids = set(list(self.aid_to_magid.keys()))
        for key, value in tmp_aid_to_refid.items():
            nr_ref += len(value)
            if value:
                non_empty_aid_to_refid[key] = value
                continue
            elif key in matched_aids:
                # Get a list of Arxiv IDs that are matched to a MAG ID but for which no reference was found
                empty_aid_to_refid.append(key)
                empty += 1

        # Store for later use
        self.matched_aids_without_ref = empty_aid_to_refid

        log.info(("Original unique MAG entries that are matched: {}. For {} arxiv Papers matched to these MAG IDs" +
                  " no references could be found ({:.2%}). " +
                  " Overall References (with duplicates): {}. Ref-Avg. for arxiv paper: {}").format(
            len(matched_mid_set), empty, empty / len(matched_aids),
            nr_ref, nr_ref / len(non_empty_aid_to_refid)))

        # Get reference overall
        refids_list = []
        for mid, refids in non_empty_aid_to_refid.items():
            refids_list += refids

        # Make a set from refids which makes it only consists of unique values
        refids_unique = set(refids_list)

        # Print some stats
        log.info("Found {} unique references by arxiv papers in MAG. Duplicate-%: {:.2%}".format(
            len(refids_unique), (len(refids_list) - len(refids_unique)) / len(refids_list)))

        self.aid_to_ref_magids = non_empty_aid_to_refid
        self.unique_ref_magids = refids_unique

        return nr_ref

    def get_references_data(self):
        """
        Collect DOI (if exists), titles and arxiv id (if known) for all papers that were referenced by an arxiv paper
        """

        # Get dict to match mag_id to arxiv id
        magid_to_data = {}

        ref_mid_matched_to_aid = 0

        # Parse line by line
        log.info("Gather data for {} unique references in Papers.txt [Be patient it has 102800000+ lines]".format(
            len(self.unique_ref_magids)))
        with open(os.path.join(MAG_BASE, "Papers.txt")) as f:
            for counter, line in enumerate(f):
                # Only update count after 10000000 entries
                if counter % 10000000 == 0:
                    log.info("Processed {} lines so far".format(counter))
                # Get content
                content = line.split("\t")
                mag_id = content[0]

                # len >= 4 check is needed as !one! entry of the dataset is wrong and does not have all fields
                if (len(content) >= 5) and (mag_id in self.unique_ref_magids):
                    # Match and store result
                    doi = content[2]
                    paper_title = content[4]
                    original_title = content[5]
                    # Arxiv ID is know If at some point this mag was found in any of our matching even if not used later
                    arxiv_id = self.magid_to_aid.get(mag_id, None)
                    if arxiv_id:
                        ref_mid_matched_to_aid += 1
                    magid_to_data[mag_id] = [doi, paper_title, original_title,
                                             arxiv_id]

        # Check emptiness
        nr_ref_ids = len(self.unique_ref_magids)
        nr_found_ref_ids = len(magid_to_data)

        # Stats
        log.info(("Found data for {} referenced MAG IDs ({:.2%}). To {} of these MAG IDs an arxiv ID was matched" +
                  " ({:.2%}). Unable to match {} MAG IDs to MAG data.").format(
            nr_found_ref_ids, nr_found_ref_ids / nr_ref_ids, ref_mid_matched_to_aid,
                              ref_mid_matched_to_aid / nr_found_ref_ids, nr_ref_ids - nr_found_ref_ids))

        self.magid_to_data = magid_to_data


def load_metadata(filename):
    log.info("Start reading {}".format(filename))
    with open(os.path.join(META, filename)) as f:
        data = json.load(f)

    return data


def save_metadata(data, filename):
    filename = os.path.join(META, filename)
    log.info("Start saving {}".format(filename))
    with open(filename, 'w+') as f:
        json.dump(data, f)
