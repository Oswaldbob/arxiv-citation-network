# Network Builder

Code to build/extend the arxiv citation network based on the data we collected.

## Notes

* Our Network won't have version numbers unlike the network created by Bierbaum's work which still includes version
  numbers in the .json but striped it for the network later on.
* Unlike the network created by Bierbaum from the .json, we do not included arxiv IDs in the final network for which the
  ID does not exist in our metadata set.

## Resource usage

In its current non-memory optimized state, the script requires $\sim$10 GB of RAM because, in its essence, it has to
load all files created so far and copy them. Implementing batching for this would have been possible but a lot more
complicated to implement and therefore not worth the effort as we have machines with at least 10 GB RAM at our disposal.

# Problems

## Bierbaum's Work (ArXiv Internal Citation Network)

The output of Bierbaum's work has around 26586 referenced Arxiv IDs that do not actually exist in the network itself.
These were created by parsing/conversion errors most likely. For example: "hep-th/0211416" instead of "hep-ph/0211416".

## Arxiv Metadata

The arxiv metadata does not have the entry "acc-phys/9607002". However, it is a valid entry on the website and from our
downloads. As a result, our code will trim this ID in the cleaning step. As we are seeing the metadata as a "ground
truth" regarding ArXiv IDs at any other point.

## MAG to Arxiv Matching

* DOI or Title duplicates in the arxiv dataset are ignored when merging. DOI duplicates must be artifacts, hence they
  can be safely ignored. Title duplicates could come from different papers, but the amount of title duplicates is
  already too small (0.19% <1%) to be relevant. Additionally, for all investigated duplicates, the duplicated titles
  belong to the same paper that was simply uploaded twice to arxiv.
* Since the MAG Extractor is only concentrated on matching MAG IDs to a set of not-yet matched Arxiv IDs it might miss
  assigning referenced MAG Papers an arxiv ID. This is fixed by preprocessing the data and matching arxiv IDs to
  potential MAG papers by DOI and Title
* Similar the set of referenced external non-arxiv MAGs has a very small percentage of title duplicates (#14236, 0.35% <
  1%). Therefore, here we also decided to ignore duplicates for simplicity reasons as our external papers are only
  identified by their title. In other words, we need to use the title (in all lowercase without whitespaces) as the ID
  of external papers. Otherwise, we can not merge the results of different methods since each method has different
  internal IDs and/or no other metadata to identify that the data references the identical object.
  * Ignoring the duplicates is done implicitly as "external papers" are referenced based on title. Hence, if more than
    one MAG ID has the same title, they will not make an impact as the title is already in the list of external papers.
  * Furthermore, the title duplicates are after investigation of a small subset related to duplicate entries in the MAG
    where one entire has a DOI and the other not.
  * Lastly, the duplicates of the MAG titles create ~500k (~1.3%) references that are not copied over to our citation
    graph because a paper cites two MAG IDs which correspond to (presumably the same) paper but which have the same
    title in the MAG
* We need to add internal arxiv papers based on MAG since the data so far is based on the successfully downloaded ones,
  but the MAG results are based on the metadata

## Parsed Data

* The name of titles seems to have uni-code errors quite often. A possible extension in the future could be to add a
  step that removes such problems in the preprocessing.
* Results of this dataset are only added carefully as this is perhaps the most unsafe method we are using.
* Due to a bug in the MAGE, aids_without_ref.json included also the IDs that were not matched. This does not change the
  results since when this JSON is merged, the IDs that were not matched are already included.

## Overall

* We are using simple title matching (no whitespaces all lower cases) to match titles. Alternatives like an edit
  distance would have been more appropriated but are computationally not plausible in our implementation. Accordingly,
  re-implementations in C++ or alternatives might provide better results.

# Results

## File Format

The data is contained in a JSON file 2.14GB in size. The format is a two-entry dictionary of \{'arxiv\_papers':\{dict
of *ArXivID*:[list of internal citations, list of external citations]\}, 'external\_papers':[list of external papers]\}.
We provide a list of external papers as shorthand for creation of a network structure, indexed on title to stay
consistent between MAGE results and parser hits. The arXiv-internal papers are indexed on arXiv-ID and each have two
lists of references attached, again split into internal/external, whereby external citations are given by titles and
internal citations by arXiv ID.

## Results from example run on all our so-far collected data

Bierbaum Size original: 1791470;

* Only final result (bierbaum + parser + mage) was post processed such that citations referring non-existing edges were
  removed. For the other this would have been not logical, as these are on purpose not trying to be well-defined graphs

Start:

* [Nodes] Number of Arxiv Papers 0; Number of External Papers 0;
* [Edges] Number of Citations of Arxiv Papers 0 (Internal); Number of Citations of external Papers 0 (External);

Bierbaum's Results:

* [Nodes] Number of Arxiv Papers 1791469; Number of External Papers 0;
* [Edges] Number of Citations of Arxiv Papers 10038069 (Internal); Number of Citations of external Papers 0 (External);

MAGE Results:

* [Nodes] Number of Arxiv Papers 1409753; Number of External Papers 4094942;
* [Edges] Number of Citations of Arxiv Papers 18391628 (Internal); Number of Citations of external Papers 20424068 (
  External);

Parser Results:

* [Nodes] Number of Arxiv Papers 383956; Number of External Papers 2017552;
* [Edges] Number of Citations of Arxiv Papers 975816 (Internal); Number of Citations of external Papers 4489784 (
  External);

MAGE + Bierbaum's Results:

* [Nodes] Number of Arxiv Papers 1793790; Number of External Papers 4094942;
* [Edges] Number of Citations of Arxiv Papers 23246360 (Internal); Number of Citations of external Papers 20424068 (
  External);

MAGE + Parser Results:

* [Nodes] Number of Arxiv Papers 1793709; Number of External Papers 5570016;
* [Edges] Number of Citations of Arxiv Papers 19367444 (Internal); Number of Citations of external Papers 24913852 (
  External);

Parser + Bierbaum's Results:

* [Nodes] Number of Arxiv Papers 1791473; Number of External Papers 2017552;
* [Edges] Number of Citations of Arxiv Papers 10727152 (Internal); Number of Citations of external Papers 4489784 (
  External);

MAGE + Bierbaum's + Parser Results:

* [Nodes] Number of Arxiv Papers 1793794; Number of External Papers 5570016;
* [Edges] Number of Citations of Arxiv Papers 23915005 (Internal); Number of Citations of external Papers 24913852 (
  External);

### Other

* Before adding MAG Data, the Citation Network had 10038107 arxiv and 0 external citations. Using the MAG Data, 13208291
  arxiv citations (33.59% of all MAG References) and 20424068 external citations (51.93% of all MAG References) were
  added (Here one can read: citations = edges). Consequently, 5694829 (14.48%) of the MAG reference were already in the
  network by previous work or a caused by title duplicates. Furthermore, the previous work was able to find 4343278
  citations not found by the MAG. In other words, 43.27% of the references generated by previous work were not found in
  the MAG
* Needed to add 2321 Arxiv IDs that are in the MAG data but not in the network
* Title Duplicates in external non-arxiv Papers from MAG: 14236 (0.35%)
* Cleaned 26586 bad Arxiv IDs from Bierbaum's results (e.g. parsing of Regex failed for these references)
* Parser-AIDs-Not-Matched: Overall references before preprocessing 1998858, afterwards 1866467. Extracted overall
  internal (arxiv)
  references: 460067; Extracted overall external references 1406400
* Parser-AIDs-Without-REF: Overall references before preprocessing 7239735, afterwards 5465600. Extracted overall
  internal (arxiv) references: 975816; Extracted overall external references 4489784.
  
