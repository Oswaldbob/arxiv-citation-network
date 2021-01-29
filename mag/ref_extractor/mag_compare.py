# Code used to compare different methods of the MAGE
import log_config_util
import mage as mage_utils
from mage import MAGE

log = log_config_util.get_logger("main")

# Extraction Pipeline using MAGE
log.info("Get IDs and sample")
id_doi_title_dict = mage_utils.load_metadata("arxiv_id_to_doi_title.json")
sampled_aids = mage_utils.load_metadata("sampled_aids_100k.json")

# Remove versions
sampled_aids_without_version = set([aid.rsplit("v", 1)[0] for aid in sampled_aids])

# Filter for only entries of sampled aids
sampled_id_doi_title_dict = {aid: value for aid, value in id_doi_title_dict.items() if
                             aid in sampled_aids_without_version}
len_sampled = len(sampled_id_doi_title_dict)

# DOI
log.info("Got IDs - Start Test for DOI Matching")
mage = MAGE(sampled_id_doi_title_dict)
mage.match_doi()
nr_ref = mage.get_reference_ids()

doi_aids = set(mage.aid_to_magid.keys())
doi_matched_nr = len(mage.aid_to_magid)
doi_references_unique_nr = len(mage.unique_ref_magids)
doi_references_overall_nr = nr_ref

base_stats = "[Overall] #Arxiv IDs: {}. #DOIs {} ({:.2%}). #Unqiue Titles {} ({:.2%}).".format(
    len(mage.aid_set), len(mage.doi_set), len(mage.doi_set) / len(mage.aid_set),
    len(mage.title_set), float(len(mage.title_set) / len(mage.aid_set)))

# URL
log.info("Start Test for URL Matching")
mage = MAGE(sampled_id_doi_title_dict)
mage.match_url()
nr_ref = mage.get_reference_ids()

url_aids = set(mage.aid_to_magid.keys())
url_matched_nr = len(mage.aid_to_magid)
url_references_unique_nr = len(mage.unique_ref_magids)
url_references_overall_nr = nr_ref

# Title
log.info("Start Test for Start Test for Title Matching")
mage = MAGE(sampled_id_doi_title_dict)
mage.simple_match_title()
nr_ref = mage.get_reference_ids()

title_aids = set(mage.aid_to_magid.keys())
title_matched_nr = len(mage.aid_to_magid)
title_references_unique_nr = len(mage.unique_ref_magids)
title_references_overall_nr = nr_ref

# All Combined
log.info("Start Test for All Matching")
mage = MAGE(sampled_id_doi_title_dict)
mage.match_doi()
mage.match_url()
mage.simple_match_title()
nr_ref = mage.get_reference_ids()

all_matched_nr = len(mage.aid_to_magid)
all_references_unique_nr = len(mage.unique_ref_magids)
all_references_overall_nr = nr_ref
log.info("Finished MAG Processing")

# Post Processing - Get stats about overlapping of "same" matched papers
diff_title = (title_aids - url_aids) - doi_aids
title_unique_matches = len(diff_title)

diff_url = (url_aids - doi_aids) - title_aids
url_unique_matches = len(diff_url)

diff_doi = (doi_aids - title_aids) - url_aids
doi_unique_matches = len(diff_doi)

title_url_duplicates = len(set(title_aids) & set(url_aids))  # Idea from here: https://stackoverflow.com/a/4775027
title_doi_duplicates = len(set(title_aids) & set(doi_aids))
doi_url_duplicates = len(set(doi_aids) & set(url_aids))
all_duplicates = len(set(doi_aids) & set(url_aids) & set(title_aids))

# Results
log.info("##### Printing Results #####")
log.info(base_stats)

log.info(("[{}] Matched: {} ({:.2%}); Unique Matches: {} ({:.2%});" +
          " References-Overall: {}; References-Unique: {} (Unique-%: {:.2%}); ").format(
    "DOI",
    doi_matched_nr, doi_matched_nr / len_sampled, doi_unique_matches, doi_unique_matches / doi_matched_nr,
    doi_references_overall_nr,
    doi_references_unique_nr, doi_references_unique_nr / doi_references_overall_nr))

log.info(("[{}] Matched: {} ({:.2%}); Unique Matches: {} ({:.2%});" +
          "References-Overall: {}; References-Unique: {} (Unique-%: {:.2%}); ").format(
    "URL",
    url_matched_nr, url_matched_nr / len_sampled, url_unique_matches, url_unique_matches / url_matched_nr,
    url_references_overall_nr,
    url_references_unique_nr, url_references_unique_nr / url_references_overall_nr))

log.info(("[{}] Matched: {} ({:.2%}); Unique Matches: {} ({:.2%});" +
          "References-Overall: {}; References-Unique: {} (Unique-%: {:.2%}); ").format(
    "TITLE",
    title_matched_nr, title_matched_nr / len_sampled, title_unique_matches,
                      title_unique_matches / title_matched_nr,
    title_references_overall_nr,
    title_references_unique_nr, title_references_unique_nr / title_references_overall_nr))

log.info(("Title-URL-Duplicates-#: {}, this is {:.2%} of all TITLE- and {:.2%} of all URL-matches. \n" +
          "Title-DOI-Duplicates-#: {}, this is {:.2%} of all TITLE- and {:.2%} of all DOI-matches. \n" +
          "URL-DOI-Duplicates-#: {}, this is {:.2%} of all URL- and {:.2%} of all DOI-matches. \n" +
          "Intersection of all Duplicates: {}.").format(
    title_url_duplicates, title_url_duplicates / title_matched_nr, title_url_duplicates / url_matched_nr,
    title_doi_duplicates, title_doi_duplicates / title_matched_nr, title_doi_duplicates / doi_matched_nr,
    doi_url_duplicates, doi_url_duplicates / url_matched_nr, doi_url_duplicates / doi_matched_nr,
    all_duplicates))

log.info("[{}] Matched: {} ({:.2%}); References-Overall: {}; References-Unique: {} (Unique-%: {:.2%}); ".format(
    "All Combined",
    all_matched_nr, all_matched_nr / len_sampled,
    all_references_overall_nr,
    all_references_unique_nr, all_references_unique_nr / all_references_overall_nr))
