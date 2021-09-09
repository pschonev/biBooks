Repository to create bilingual e-books from source texts in two different languages using python

Steps:

1. Get source data (e.g. web scraping)

2. Clean the data (notebooks/prepare_data.ipynb)

3. Sentence tokenization 

    - Russian razdel = https://github.com/natasha/razdel 

    - English pySBD = https://github.com/nipunsadvilkar/pySBD

4. Sentence alignment

    - hunalign seems to have been popular but the performance was terrible + you need to create your own dictionary for input/output language word pairs

    - vecalign (https://github.com/thompsonb/vecalign) works incredibly well
        - first create n (e.g. 10) possible overlaps for each sentence (concatenations with following sentences) with vecalign/overlap.py
        - then embed the overlap sentence file using LASER (https://github.com/facebookresearch/LASER). this gets multilingual sentence embeddings in 93 languages, making the embeddings comparable to one another 
        - back to vecalign run vecalign/vecalign.py on all 6 files - the original source with sentence tokenization, the overlap sentence file and the embeddings for both source and target language - and you will get a file that indicates the alignments of the sentences
        - now take the alignment file combined with source and target language files with tokenized sentences to create a combined tab seperated file (tsv) of aligned sentences (see notebooks/alignments_to_text.ipynb) 

5. Convert the resulting tsv of aligned sentences into a html to use with calibre with the hun2htmlgray14.py script (see https://www.mobileread.com/forums/showthread.php?t=39719#8) and make sure the lrstyle.css (https://languagefixation.wordpress.com/2011/02/23/how-to-create-parallel-texts-for-language-learning-part-2/) is in the same folder as the html file for the next step

6. with calibre installed run ebook-convert to get an ebook file with the format of your choice (epub, mobi, etc)


Optional: For Russian, use UDAR (https://github.com/reynoldsnlp/udar) to create a file with stresses added from the source file with sentence tokenization and use it when creating the combined text file at the end of step 4. instead of the source file with sentence tokenization

Optional2: Create a MOBI dictionary from wiktionary https://github.com/nyg/wiktionary-to-kindle