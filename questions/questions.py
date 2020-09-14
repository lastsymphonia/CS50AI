import nltk
import sys

import string
import os
import math
from collections import Counter

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    file_loc = {}
    # open directory and read files into dict format filename:contents
    with os.scandir(directory) as files:
        for file in files:
            with open(file) as f:
                doc = f.read()
                file_loc[file.name] = doc
    return file_loc


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    doc = document.translate(str.maketrans('', '', string.punctuation)) # to remove punctuation
    doc = nltk.word_tokenize(doc)
    doc = [word.lower() for word in doc if word.lower() not in nltk.corpus.stopwords.words("english")] # remove stopwords
    return doc


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    total_docs = len(documents.keys())
    # getting all the unique words in documents
    words = set([word for docs in documents.values() for word in docs])
    # getting idf for words using formula
    idf = {}
    for word in words:
        doc_count = 0
        for docs in documents:
            if word in documents[docs]:
                doc_count += 1
        idf[word] = math.log(total_docs / doc_count)
    return idf


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # count of words in each document, if they are in query (term freq)
    doc_word_count = {k:Counter([word for word in v if word in query]) for k,v in files.items()}

    # getting tf-idf for each word
    doc_tfidf = {}
    for doc in doc_word_count.keys():
        for word in doc_word_count[doc]:
            doc_word_count[doc][word] *= idfs[word]
        doc_tfidf[doc] = sum(doc_word_count[doc].values())
    # gets a sorted dict, then taking only key values (filename) into list.
    sorted_tfidf = [k for k, v in sorted(doc_tfidf.items(),reverse=True ,key=lambda item: item[1])]
    return sorted_tfidf[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # for getting idfs and qt density
    get_idf = lambda value: [idfs[word] for word in set(value) if word in query] # using set(value) to ensure no doublecount of idf
    get_qt_density = lambda value: (len([word for word in value if word in query]) / len(value))
    sentence_idf = {k:(sum(get_idf(v)), get_qt_density(v)) for k,v in sentences.items()}
    # first sorts by idf (item[1][0]), then qt (item[1][1])
    sorted_tfidf = [k for k, v in sorted(sentence_idf.items(),reverse=True ,key=lambda item: (item[1][0], item[1][1]))]
    return sorted_tfidf[:n]


if __name__ == "__main__":
    main()
