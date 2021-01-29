import os
import json
import time

from parse_references import log_config_util


log = log_config_util.get_logger("parser")


def copy(aids, source_folder, dist_folder):
    """
    Copy PDFs to parse from source directory to temporal folder
    @:param: aids List in shape of ['arxiv_id', ...] as JSON, arxiv_id does not contain suffix with version
    """
    log.info("Start copying pdfs")
    start = time.time()

    with open(aids, 'r') as f:
        arxiv_ids = json.load(f)

    os.system('mkdir {}'.format(dist_folder))
    for i, aid in enumerate(arxiv_ids):
        os.system('cp {} {}'.format(os.path.join(source_folder, aid.replace('/', '_') + '*'), dist_folder))
        if i % 10000 == 0:
            log.info("{} papers have been copied. Elapsed time (in minutes): {:.2}".format(i, (time.time() - start)/60.))

    log.info("Finish copying pdfs. Elapsed time (in minutes): {:.2}".format((time.time() - start)/60.))


def parse(source_folder, output_folder, science_parse_jar):
    """
    Run Science Parse on papers in temp_folder
    @:param: science_parse_jar Path to jar file
    """
    log.info("Start parsing pdfs")
    start = time.time()

    os.system('mkdir {}'.format(output_folder))
    os.system('java -Xmx6G -jar {} {} -o {}'.format(science_parse_jar, source_folder, output_folder))

    log.info("Finish parsing pdfs. Elapsed time (in minutes): {:.2}".format((time.time() - start)/60.))


def extract_references(source_folder, output):
    """
    Extract references from parsing results and put them in a single JSON
    Output file: {'arxiv_id':[{'author' : 'author_name', 'title': 'paper title'}]}
    :param source_folder: path to a folder with parsing results
    :param output: name of file to write results
    """

    log.info("Start extracting references")
    start = time.time()

    file_names = os.listdir(source_folder)
    result = {}
    for file in file_names:
        with open(os.path.join(source_folder, file), 'r+') as f:
            try:
                parsed_data = json.load(f)
            except ValueError as e:
                log.warn('Reading {} failed: {} {} '.format(file, type(e).__name__, str(e)))
                continue

        x = []
        for record in parsed_data['metadata']['references']:
            temp = {}
            temp['author'] = record['author']
            temp['title'] = record['title']
            x.append(temp)

        result[file[:-9]] = x

    with open(output, 'w+') as f:
        json.dump(result, f)

    log.info("Finish extracting references. Elapsed time (in minutes): {:.2}".format((time.time() - start)/60.))

