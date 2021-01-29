# Some deprecated code for title matching stored for the sake of completeness and transparency

def match_title_v3(self, slice_size_n=1000):
    """Find MAG IDs based on title (deprecated test code not used in current implementation)"""

    # Get sets for look up
    aids_not_matched = set(self.aids_not_matched())
    mids_matched = set(self.mids_matched())
    arxiv_titles_to_match = set(
        [self.aid_to_title[aid] for aid in aids_not_matched][:650000])
    pre_length = len(arxiv_titles_to_match)

    # Parse line by line

    with open(os.path.join(MAG_BASE, "Papers.txt")) as f:
        counter = 0
        # Introduce batching of lines to check multiple titles at once
        for n_lines in iter(lambda: tuple(islice(f, slice_size_n)), ()):

            # Only update count after certain amount of entries and update counter
            if counter % slice_size_n == 0:
                log.info("Processed {} lines so far".format(counter))
                if counter > 0:
                    break
            counter += slice_size_n

            # Match mag titles to mid for later use, this will remove duplicates
            # Duplicates are removed because if the title has the same name the last entry with the title will set the value for the mid
            tmp_mtitle_to_mid = {}
            for line in n_lines:
                content = line.split("\t")
                mid = content[0]

                # Skip if this mid is already matched (hence it does not need any further matching)
                # len < 4 check is needed as !one! entry of the dataset is wrong and does not have all fields
                if mid in mids_matched or (len(content) < 4):
                    continue

                paper_title = content[4]
                original_title = content[5]

                # Both titles are matched to same mag id so if one is found it works
                tmp_mtitle_to_mid[paper_title] = mid
                tmp_mtitle_to_mid[original_title] = mid

            # Get list of all titles (duplicates removed due to using tmp_title_to_mid)
            relevant_mag_titles = list(tmp_mtitle_to_mid.keys())

            # Skip if list is empty
            if not relevant_mag_titles:
                continue

            # Match papers
            matched, found_matches = self.match_titles_core(relevant_mag_titles, arxiv_titles_to_match)

            if matched:
                for match in found_matches:
                    # Match title to aids and mid
                    arxiv_ids = self.title_to_aids[match[1]]
                    mag_id = tmp_mtitle_to_mid[match[0]]

                    # Save mag_id for all matched aids
                    for arxiv_id in arxiv_ids:
                        self.magid_to_aid[mag_id] = arxiv_id
                        self.aid_to_magid[arxiv_id] = mag_id

                    # Removed matched title from arxiv titles that still need to be matched
                    arxiv_titles_to_match.discard(match[1])

    if self.stats:
        log.info("Was trying to match {} titles. Was able to match {} titles ({:.2%}).".format(
            pre_length, pre_length - len(arxiv_titles_to_match),
                        (pre_length - len(arxiv_titles_to_match)) / pre_length))
        self.log_matching_stats()


def match_titles_core(self, relevant_mag_titles, arxiv_titles):
    """
    Tool to match arxiv title to possible mag titles
    :param relevant_mag_titles: [title1, title2,...]
    :param arxiv_titles: titles to which the titles of the paper need to be compared
    :return: true/false, [(mag_title, arxiv_title),...]
    """

    cutoff = self.title_matching_cutoff
    found_matches = []
    # Goal of this re-implementation reduce iterations through set of arxiv_titles
    for a_title in arxiv_titles:
        title_matches = difflib.get_close_matches(a_title, relevant_mag_titles, cutoff=cutoff, n=1)

        if title_matches:
            # Matches with high enough score were found and the best returned
            found_matches.append((title_matches[0], a_title))

    # If empty and no match where found, return False
    if not found_matches:
        return False, None

    # See below why this
    return True, found_matches


def compare_titles(self, paper_titles, to_compare_titles):
    """
    Compare titles using a measure and chose the most similar title to return if a threshold is reached
    :param paper_titles: titles of a given paper (best sorted for most accurate title)
    :param to_compare_titles: titles to which the titles of the paper need to be compared
    :return: true/false, best matched title
    """

    # Brute-force method as one compares these strings to all others each time this is called
    best_matches = []
    for title in paper_titles:
        # Implementation 2 using levenshtein distance (Idea from: https://stackoverflow.com/a/15398763 and https://codereview.stackexchange.com/a/217067) [might be a lot faster since underlying usage of c]
        title_len = len(title)
        # This looks complicated but is required to use list comprehension for speed up
        best_match = sorted([[percentage, compare_title] for compare_title in to_compare_titles
                             if (percentage := (max(title_len, compare_title[1])
                                                - levenshtein_distance(title, compare_title[0])) / max(title_len,
                                                                                                       compare_title[
                                                                                                           1]))
                             and percentage >= self.title_matching_cutoff], key=lambda x: x[0])

        if best_match:
            best_matches.append(best_match[0][1])

    if not best_matches:
        return False, None

    # See below why this
    return True, best_matches[0]
