import metadata
import log_config_util
import mag

log = log_config_util.get_logger("main")

log.info("Start Metadata Processing")
id_doi_dict = metadata.process_metadata()
metadata.save_metadata(id_doi_dict)
log.info("Finished Preprocessing")
