import log_config_util
from arxivcitationnetwork import ArxivCitationNetwork
import merger

log = log_config_util.get_logger("main")

# Important init
metadata_aid_to_doi_title = log_config_util.load_metadata("arxiv_id_to_doi_title.json")

# Empty
citation_network = ArxivCitationNetwork()
start_stats = citation_network.get_stats()

# Bierbaum
merger.merge_bierbaum_network(citation_network, metadata_aid_to_doi_title)
bierbaum_stats = citation_network.get_stats()

# MAGE + Bierbaum
merger.merge_mag_data(citation_network, metadata_aid_to_doi_title)
mag_bierbaum_stats = citation_network.get_stats()

# MAGE + Bierbaum + Parser
parsed_aids_not_matched = log_config_util.load_metadata("parsed_aids_not_matched.json")
merger.merge_parser_data(citation_network, metadata_aid_to_doi_title, parsed_aids_not_matched)
parsed_aids_without_ref = log_config_util.load_metadata("parsed_aids_without_ref.json")
merger.merge_parser_data(citation_network, metadata_aid_to_doi_title, parsed_aids_without_ref)
# Post-Processing
citation_network.clean_arxiv_citations()
citation_network.clean_external_citations()
mag_bierbaum_parser_stats = citation_network.get_stats()
# Get output for all combined
json_output = citation_network.to_json()

# Further tests which are duplicates of the code above but result in useful information
# Only MAGE
citation_network = ArxivCitationNetwork()
merger.merge_mag_data(citation_network, metadata_aid_to_doi_title)
mag_stats = citation_network.get_stats()
# MAGE + Parser
merger.merge_parser_data(citation_network, metadata_aid_to_doi_title, parsed_aids_not_matched)
merger.merge_parser_data(citation_network, metadata_aid_to_doi_title, parsed_aids_without_ref)
mag_parser_stats = citation_network.get_stats()

# Only Parser
citation_network = ArxivCitationNetwork()
merger.merge_parser_data(citation_network, metadata_aid_to_doi_title, parsed_aids_not_matched)
merger.merge_parser_data(citation_network, metadata_aid_to_doi_title, parsed_aids_without_ref)
parser_stats = citation_network.get_stats()

# Parser + Bierbaum
citation_network = ArxivCitationNetwork()
merger.merge_bierbaum_network(citation_network, metadata_aid_to_doi_title)
merger.merge_parser_data(citation_network, metadata_aid_to_doi_title, parsed_aids_not_matched)
merger.merge_parser_data(citation_network, metadata_aid_to_doi_title, parsed_aids_without_ref)
bierbaum_parser_stats = citation_network.get_stats()

# Print stats
log.info("#### Print Results ####\n" +
         "Start: \n" + start_stats +
         "\nBierbaum's Results: \n" + bierbaum_stats +
         "\nMAGE Results: \n" + mag_stats +
         "\nParser Results: \n" + parser_stats +
         "\nMAGE + Bierbaum's Results: \n" + mag_bierbaum_stats +
         "\nParser + Bierbaum's Results: \n" + bierbaum_parser_stats +
         "\nMAGE + Parser Results: \n" + mag_parser_stats +
         "\nMAGE + Bierbaum's + Parser Results: \n" + mag_bierbaum_parser_stats)

# Output
log_config_util.save_metadata(json_output, "citation_network.json")
