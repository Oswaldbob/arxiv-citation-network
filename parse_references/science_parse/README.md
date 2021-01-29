## Overview
This document describes installation process of Science Parse, its configuration and input/output details.

### Install Science Parse
https://github.com/allenai/science-parse  
Download source code and build jar file using `sbt`  
Installation details and usage in CLI mode: https://github.com/allenai/science-parse/blob/master/cli/README.md

### Configuration
Create `config.ini` based on provided `example.config.ini`  
`pdfs_to_parse` path to a directory which contains source PDF files  
`parsing_results` path to a directory where to save parsed references  
`science_parse_jar` path to the corresponding jar-file

### science_parse.py
Executes Science Parse in CLI mode, writes JSONs with parsed references to `parsing_results`.

### Input and output
Input is PDF or path to directory with multiple PDFs to parse, output is JSON, each JSON file corresponds to one PDF:
```
{
  "title" : "Text segmentation based on semantic word embeddings",
  "author" : [ "Alexander A. Alemi", "Paul Ginsparg" ],
  "venue" : "CoRR, abs/1503.05543,",
  "citeRegEx" : "Alemi and Ginsparg.,? \\Q2015\\E",
  "shortCiteRegEx" : "Alemi and Ginsparg.",
  "year" : 2015
}
```

### Notes
* Some dependencies errors may arise: https://stackoverflow.com/questions/61271015/sbt-fails-with-string-class-is-broken  
* "Can parse multiple files at the same time. You can parse thousands of PDFs like this. It will try to parse as many of them in parallel as your computer allows."
* There is a new version of this parser. It is declared to be more precise but slower.

