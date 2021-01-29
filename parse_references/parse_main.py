from parse_references import log_config_util
from parse_references import parse_pdfs


parse_pdfs.copy(log_config_util.get_aids_to_copy(), log_config_util.get_origin_pdfs(), log_config_util.get_pdfs_to_parse())

parse_pdfs.parse(log_config_util.get_pdfs_to_parse(), log_config_util.get_parsing_results(), log_config_util.get_science_parse_jar())

parse_pdfs.extract_references(log_config_util.get_parsing_results(), log_config_util.get_extracted_references())
