import log_config_util
import mage as mage_utils
from mage import MAGE

log = log_config_util.get_logger("main")

# Extraction Pipeline using MAGE
log.info("Get IDs")
id_doi_title_dict = mage_utils.load_metadata("arxiv_id_to_doi_title.json")
log.info("Got IDs - Start MAG Processing")
mage = MAGE(id_doi_title_dict)
# Match Papers
mage.match_doi()
mage.match_url()
mage.simple_match_title()

# Get not matched_list
mage_utils.save_metadata(mage.get_not_matched(), "aids_not_matched.json")

# Get references
mage.get_reference_ids()
mage.get_references_data()
mage_utils.save_metadata(mage.magid_to_data, "magid_to_data.json")  # self.magid_to_data
mage_utils.save_metadata(mage.aid_to_ref_magids, "aid_to_ref_magids.json")

# Get no reference list
mage_utils.save_metadata(mage.matched_aids_without_ref, "aids_without_ref.json")

log.info("Finished MAG Processing")
