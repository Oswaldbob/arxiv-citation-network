# Code for analysis

# Random Sampling -> 'sample_test_data'

Sample 100000 IDs (corresponding to papers as PDF) from our dataset. It is important to note that the arxiv papers have
a categorical and temporal difference. The properties of the papers - like having a DOI, how often they are cited and if
they cite arXiv papers - might change across time or different categories. For example, the computer science papers
might be more present on arxiv than economics papers. Similar, in 2007 arxiv was not as popular as in 2020 and thus
other arxiv papers were cited less often. However, for our project we think that doing random sampling overall papers (
i.e. across all categories and all time) provides enough randomness to avoid drastic statistical problems from these
differences. Additionally, these differences are not explicitly relevant for our analysis. A more detailed look at time
and categorical differences for this analysis might be of interest in the future.

# Method Analysis

## Quantitative comparison

The following results compare the amount of references that ours method can extract

* Dataset used: 100k sampled (#Arxiv IDs: 100000. #DOIs 52043 (52.04%). #Unique Titles 99982 (99.98%))

### MAG

* [All Combined] Matched: 96190 (96.19%); References-Overall: 2210506; References-Unique: 1100686 (Unique-%: 49.79%);
  * [DOI-Matching] Matched: 51173 (51.17%); Unique Matches: 6010 (11.74%); References-Overall: 1538167;
    References-Unique: 760990 (Unique-%: 49.47%);
  * [URL-Matching] Matched: 57171 (57.17%); Unique Matches: 2145 (3.75%);References-Overall: 1236658; References-Unique:
    708315 (Unique-%: 57.28%);
  * [TITLE-Matching] Matched: 78454 (78.45%); Unique Matches: 18741 (23.89%);References-Overall: 1666391;
    References-Unique: 915345 (Unique-%: 54.93%);


* Duplicates/Intersection Statistic:
  * Title-URL-Duplicates-#: 45443, this is 57.92% of all TITLE- and 79.49% of all URL-matches.
  * Title-DOI-Duplicates-#: 35580, this is 45.35% of all TITLE- and 69.53% of all DOI-matches.
  * URL-DOI-Duplicates-#: 30893, this is 54.04% of all URL- and 60.37% of all DOI-matches.

* Here, matched only means that an arxiv ID was matched to an entry in the MAG. However, this does not mean that the
  output of the MAG extractor has this arxiv ID. Because, if no references are found for this entry, MAG disregards the
  match for the output and stores it in a different list ("aids_without_ref.json").

### Parser

* [Parser] Extracted from 99986 (99.99%); References-Overall: 2136611; References-Unique: 1161507 (Unique-%: 54.36%);

### Clement et al. Work

* [Clement et al.] Extracted from 100000 (100.00%); References-Overall: 559905; References-Unique: 291976 (Unique-%:
  52.15%);
  * Remark: This obviously less since only arxiv papers are regarded!

## Qualitative comparison

Idea: Use MAG DOI Data as "Ground truth", then compare other extracted references to it. Explanation: The MAG DOI Data
is guaranteed safely matched as the DOI is a unique ID uniquely identifying papers in MAG and Arxiv. Hence, we can be
sure that the match is correct between arxiv and the possible method. Furthermore, we can assume that the references
extracted from the MAG using such a match are the "most" safe data we have. Even so MA (and accordingly MAG) are based
on BING machine readers (see https://academic.microsoft.com/faq Content, Where does the data for Microsoft Academic come
from?), it is safer than other methods since MA (and accordingly MAG) is heavily moderated and feedback/community
driven. Yet, it needs to be remarked, that the data is still quite incomplete and a difference between MA and MAG
exists. In other words, MAG often only contains a concrete subset of all references and thus is similarly incomplete,
i.e. incomplete but correct. Lastly, it has the "most" results overall. Thus, it is the best we have.

* Dataset: For the Sampled 100k, 52056 have a DOI. Sample 10k of these

### Possible alternative

* We can not get a complete overview of precision for the Results of MAG, Bierbaum and the parser unless we first build
  a hand-made dataset of all references. This is out of scope for our project if we would want to test this on more than
  100 papers.

### Notes

* Treat self-references from the results separately. Bierbaum's results often included self-references to previous
  versions as the regex picked up footnotes referring to previous versions. This inflates the numbers heavily and was
  thus removed. Similar self-references do not exist in MAG. (In our final result graph these still exist since they
  are "mentionable" references). The Parser might also capture self-references, hence they are also listed separate.
* Amount of papers for Parser is not 10k as the distribution from above seems to be approached such that a few are
  missing

### Results

* [Ground Truth (GT) MAG] Entries: 10000; Overall references 292432
* [Clement et al.] Entries: 10000 (%-of-GT: 100.00%); Overall references 70675 (%-of-GT: 24.17%); Found 39355 of GT
  references (13.46%).
  * 22323 references were not in GT. This corresponds to 31.59% of all references found by Bierbaum's work.
  * Self-references: 8997
* [Parser] Entries: 9997 (%-of-GT: 99.97%); Overall references 196164 (%-of-GT: 67.08%); Found 51678 of GT references (
  17.67%).
  * 144447 references were not in GT. This corresponds to 73.64% of all references found by the Parser.
  * Self-references: 39
