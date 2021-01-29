# Overview
This document contains list of open-source parsers which were considered to be used in a project. It is possible to replace Science Parse with any other parser with wide functionality.

## List of parsers
Reference parsers can be divided into two categories: tools that are solely reference parsers (input should be a raw reference string), and tools with wider functionality (tools are able to extract references from a whole raw text).

| Wide functionality | Pure parsers |
| ------------- | ------------- |
| Grobid (java) | Anystyle-Parser |
| CERMINE  | Neural Parscit  |
| Science Parse (java, scala)| Reference Tagger |
|  ParsCit (perl) ||
|  PDFSSA4MET (python, using regex)||

### ParsCit
https://github.com/knmnyn/ParsCit  
Was not able to test it due to some perl dependencies problem.  
Input is text file, output is XML.  
Several drawbacks:
* Fails on files named with white spaces (https://github.com/knmnyn/ParsCit/issues/19)  
* Does not identify citations if "References"/"Bibliography" or other words which indicate the references section are missing (https://github.com/knmnyn/ParsCit/issues/10)  
* Author name is a single string, i.e. first and last names are not distinguished (https://github.com/knmnyn/ParsCit/issues/18)

### ParsCit Neural
https://github.com/WING-NUS/Neural-ParsCit  
Requires `WordEmbeddings with <UNK>` to run this parser.
However, the provided link is broken (https://github.com/WING-NUS/Neural-ParsCit#word-embeddings).  

### Grobid
https://grobid.readthedocs.io/en/latest/  
Input is PDF, output is XML.

### CERMINE
https://github.com/CeON/CERMINE  
Works same as Grobid, parses PDF into XML.

### Anystyle
https://github.com/inukshuk/anystyle  
Parses references but not full text.

### Reference Tagger
https://github.com/rmcgibbo/reftagger  
Parses only single reference string

### PDFSSA4MET
https://github.com/eliask/pdfssa4met
Input is PDF, output is XML.  
Written 10 years ago and depends on pdf2xml tool.
