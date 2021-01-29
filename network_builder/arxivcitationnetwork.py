def format_name_to_id(name):
    return ''.join(name.split()).lower()


class ExternalPaper:
    def __init__(self, name, doi=None, mag_id=None):
        if doi:
            # make doi values upper case
            doi.upper()

        self.name = name
        self.mag_id = mag_id
        self.doi = doi


class ArxivPaper:
    def __init__(self, arxiv_id, arxiv_citations=None, external_citations=None, doi=None, title=None):

        if arxiv_citations is None:
            arxiv_citations = []
        if external_citations is None:
            external_citations = []
        if doi:
            # make doi values upper case
            doi.upper()

        self.arxiv_id = arxiv_id
        self.arxiv_citations = list(set(arxiv_citations))  # parse to set first to make sure not duplicates exist
        self.external_citations = list(set(external_citations))  # remove duplicates
        self.doi = doi
        self.title = title

    def add_external_citation(self, title, format_title=True):
        """Adds an external citation to the arxiv paper"""
        if format_title:
            title = format_name_to_id(title)
        self.external_citations.append(title)

    def add_arxiv_citation(self, arxiv_id):
        """Add an internal arxiv citation"""
        self.arxiv_citations.append(arxiv_id)

    def remove_duplicates_in_citations(self):
        """Remove duplicates of titles or arxiv ids in the citation lists"""
        self.arxiv_citations = list(set(self.arxiv_citations))
        self.external_citations = list(set(self.external_citations))


class ArxivCitationNetwork:
    def __init__(self):
        # Dict that sores arxiv id as key and ArxivPaper object as value
        self.arxiv_papers = {}
        self.external_papers = {}

    def add_arxiv_paper(self, arxiv_id, a_cites=None, ex_cites=None, doi=None, title=None):
        """Adds arxiv paper to the network"""

        # Add object to dict - we are ignoring arxiv ID duplicates here on purpose
        self.arxiv_papers[arxiv_id] = ArxivPaper(arxiv_id, arxiv_citations=a_cites, external_citations=ex_cites,
                                                 doi=doi, title=title)

    def clean_arxiv_ids(self, valid_arxiv_ids):
        """Remove all references and entries that have bad arxiv IDs"""

        valid_arxiv_ids = set(valid_arxiv_ids)  # Make to set for performance
        faulty_ids = []  # List of arxiv IDs that are "wrong" according to the valid list

        # Remove entries
        invalid_entries = set(self.arxiv_papers.keys()) - set(valid_arxiv_ids)
        faulty_ids += list(invalid_entries)
        for key in invalid_entries:
            self.arxiv_papers.pop(key)

        # Remove references
        for key, arxiv_paper in self.arxiv_papers.items():

            for arxiv_id in arxiv_paper.arxiv_citations:
                # Check if reference is a valid ID
                if not (arxiv_id in valid_arxiv_ids):
                    # Remove
                    arxiv_paper.arxiv_citations.remove(arxiv_id)
                    faulty_ids.append(arxiv_id)

        return faulty_ids

    def number_arxiv_citations(self):
        """Return the number of overall arxiv citations"""
        number = 0
        for key, value in self.arxiv_papers.items():
            number += len(value.arxiv_citations)

        return number

    def number_external_citations(self):
        """Return the number of overall external citations"""
        number = 0
        for key, value in self.arxiv_papers.items():
            number += len(value.external_citations)

        return number

    def add_external_paper(self, name, doi=None, mag_id=None, format_name=True):
        """Adds non-arxiv paper to the network whereby the title in a certain format is the ID"""
        # Format name
        if format_name:
            name = format_name_to_id(name)

        # Make sure doi is None and not empty string
        if not doi:
            doi = None

        # Add object to dict - we are ignoring potential title duplicates here on purpose
        self.external_papers[name] = ExternalPaper(name, doi=doi, mag_id=mag_id)

    def to_json(self):
        """
        Transform Citation Network into one JSON file

        Possibilities:
        # Full Data
        {arxiv_papers: {arxiv_id: (internal_cites arxiv ids,external cites titles, doi, title),...},
        external_papers: [(title, mag_id, doi),...]}

        # Graph View
        {nodes: [arxiv_ids,..., titles,...], edges :{arxiv_id: (internal_cites arxiv ids,external cites titles),.. }

        # Graph View reduced - THIS FOR NOW
        {"arxiv_papers": {arxiv_id: ([arxiv ids of internal citations],[titles of external citations]),... },
        "external_papers": [title,...]}

        """

        # Build output
        output = {"arxiv_papers": {}, "external_papers": list(self.external_papers.keys())}

        arxiv_papers_only_cites = {arxiv_id: (ap_object.arxiv_citations, ap_object.external_citations)
                                   for arxiv_id, ap_object in self.arxiv_papers.items()}
        output["arxiv_papers"] = arxiv_papers_only_cites

        return output

    def get_stats(self):
        nr_ap = len(self.arxiv_papers.keys())
        nr_ep = len(self.external_papers.keys())

        nr_ac = self.number_arxiv_citations()
        nr_ec = self.number_external_citations()

        stats_string = ("[Nodes] Number of Arxiv Papers {}; Number of External Papers {}; \n" +
                        "[Edges] Number of Citations of Arxiv Papers {} (Internal);" +
                        " Number of Citations of external Papers {} (External); \n").format(
            nr_ap, nr_ep,
            nr_ac,
            nr_ec
        )

        return stats_string

    def clean_arxiv_citations(self):
        """Remove cited arxiv IDs that are not nodes itself"""

        node_aids = set(self.arxiv_papers.keys())

        for key, arxiv_paper in self.arxiv_papers.items():
            for a_id in arxiv_paper.arxiv_citations:
                if a_id in node_aids:
                    continue
                # Remove non-node citations
                arxiv_paper.arxiv_citations.remove(a_id)

    def clean_external_citations(self):
        """
            Remove cited external titles that are not nodes itself
            This should remove no external citations (edges) as they are only added based on the citation
            However, still applied as a safety measure.
        """

        node_titles = set(self.external_papers.keys())

        for key, arxiv_paper in self.arxiv_papers.items():
            for title in arxiv_paper.external_citations:
                if title in node_titles:
                    continue
                # Remove non-node citations
                arxiv_paper.arxiv_citations.remove(title)
