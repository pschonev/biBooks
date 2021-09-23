# biBooks - Automatic Creation of Bilingual eBooks

This repository allows the creation of an ebook with text passages alternating in two languages for the purpose of language learning. Matching the two texts is done using [vecalign](https://github.com/thompsonb/vecalign) which itself relies on Facebook's language agnostic sentence representations [LASER](https://github.com/facebookresearch/LASER).

## Installation

- Clone the repository and install the requirements
- Run `python download_models.py` to get the necessary LASER models
- Install [Calibre](https://calibre-ebook.com/) as this will be used to convert our generated HTML files to the desired eBook format

## Basic Usage

In general the two books have to provided in two files as a list of sentences seperated with a newline (see the [books](books/) folder for examples). There are several tools available to split a text into sentences (sentence tokenization) and generate this output format (I used [pySBD](https://github.com/nipunsadvilkar/pySBD)).

Using these two files, you can simply run `python bilingual_books.py` and provide arguments via a config file with `-c [config_path]` (see [configs](configs/) for examples) or via the command line. The result will be a finished eBook file.

Below the steps to go through are described. Note that step 1-3 have examples in the [notebooks folder](notebooks/) and 4-9 are done automatically when running `bilingual_books.py`.

###  Steps

1. Get text data in two files e.g. web scraping (see examples in [notebooks](notebooks/)) or converting eBook to txt using Calibre `ebook-convert [ebook_file] [output.txt]`

2. Clean the text data

3. Run sentence tokenization, e.g. using [pySBD](https://github.com/nipunsadvilkar/pySBD)

4. Possible overlaps of n (e.g. 10) sentences are created with vecalign/overlap.py

5.  These overlapped sentences are then embedded using LASER, making them comparable independent of their language

6. Then all 6 files (original sentences, overlaps and embeddings) are fed to the main vecalign algorithm to determine matching text passages

7. The resulting alignment file indicates which lines of the original text with sentence tokenization match which each other. This can now be used to create a combined tab seperated (.tsv) file of matching text passages

8. This .tsv file is then converted into HTML format and can be accompanied by a .css file for styling

9. With Calibre installed run `ebook-convert [HTML-file] [ebook-file]` to get an eBook file with the format of your choice (epub, mobi, etc.)

10. Finally you may want to open the eBook in Calibre and fix some issues or add additional things such as a cover pic


Optional 6a: For Russian, use UDAR (https://github.com/reynoldsnlp/udar) to create a file with stresses added from the source file with sentence tokenization and use it instead of the unstressed source file

## Background Info and Credits

During my research how to handle this problem I stumbled across [this forum post from 2016](https://www.mobileread.com/forums/showthread.php?t=39719#8) explaining how to do the same thing except with [hunalign](https://github.com/danielvarga/hunalign) instead of vecalign. However when trying hunalign the results were very poor and the dictionary creation seemed tedious. However this forum post was still helpful for my overall procedural structure and it additionally linked to [this helpful blog post](https://languagefixation.wordpress.com/2011/02/23/how-to-create-parallel-texts-for-language-learning-part-2/) where I found the HTML conversion script. So credit to the user slex and doviende who also let me use his script.



## To-Do
- better handling of paragraphs (e.g. keep paragraphs together up to a certain length or ensure a newline after a paragraph is over in the final document)
- dynamic layout inspired by [Doppeltext](https://www.doppeltext.com/en/) 
- automatically process files in eBook format (converting and cleaning newlines)
- Create a MOBI dictionary from wiktionary https://github.com/nyg/wiktionary-to-kindle