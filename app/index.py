#!/usr/bin/python
import re
import nltk
import sys
import getopt
import codecs
import os
import struct
import timeit
import html2text

# Number of documents to be indexed. None for indexing all documents.
LIMIT = 50

IGNORE_STOPWORDS = True
IGNORE_NUMBERS = True

# Ignoring single character tokens
IGNORE_SINGLES = True

# Size of the BYTE for storing the docID
BYTE_SIZE = 4

"""
indexer which produces dictionary and postings file using inverted index method
params:
    document_directory: corpus directory for indexing
    dictionary_file:    dictionary of terms
    postings_file:      postings file for all terms in dictionary
"""
def index(document_directory, dictionary_file, postings_file):
    docs = {}
    count = 1

    for docID_string in os.listdir(document_directory):
        docs[count] = docID_string
        count += 1

    docID_list = [int(docID_string) for docID_string in docs]
    docID_list.sort()

    stemmer = nltk.stem.porter.PorterStemmer()
    stopwords = nltk.corpus.stopwords.words('english')

    # Check the progress of the indexer
    docs_indexed = 0
    dictionary = {}

    # Go through each document
    for docID in docID_list:
        if (LIMIT and docs_indexed == LIMIT):
            break

        file_path = os.path.join(document_directory, str(docs[docID]))

        if (os.path.isfile(file_path)):
            file = codecs.open(file_path, encoding='utf-8', errors='ignore')
            document = file.read()

            # Get the text of the HTML document
            document = html2text.html2text(document)

            # Use NLTK to tokenize the document
            tokens = nltk.word_tokenize(document)

            # Go through each word in the document
            for word in tokens:
                # Count the frequency of the word for ranking of the results
                count = tokens.count(word)

                # Perform casefolding
                term = word.lower()

                # Ignore common words
                if (IGNORE_STOPWORDS and term in stopwords):
                    continue

                # Ignore numbers
                if (IGNORE_NUMBERS and is_number(term)):
                    continue

                # Stem the term
                term = stemmer.stem(term)

                # Remove apostrophe
                if (term[-1] == "'"):
                    term = term[:-1]

                # Ignore single character tokens
                if (IGNORE_SINGLES and len(term) == 1):
                    continue

                # Add term to the dictionary
                if (term not in dictionary):
                    dictionary[term] = [(docID, count)]
                else:
                    if (dictionary[term][-1][0] != docID):
                        dictionary[term].append((docID, count))

            docs_indexed += 1
            print 'Indexing progress: Number of files indexed = ' + str(docs_indexed)
            file.close()

    # Open files for writing
    dict_file = codecs.open(dictionary_file, 'w', encoding='utf-8')
    post_file = open(postings_file, 'wb')

    # For easy access of the particular postings list in the posting file
    byte_offset = 0

    # Write list of docIDs indexed to first line of dictionary
    dict_file.write('Indexed from docIDs:')

    for i in range(docs_indexed):
        dict_file.write(str(docID_list[i]) + ',')
    dict_file.write('\n')

    # Create dictionary file and postings file
    for term, postings_list in dictionary.items():
        # Document frequency
        df = len(postings_list)

        # Write each posting into postings file
        for docID, count in postings_list:
            # Pack docID into a byte array of size 4
            posting = struct.pack('I', docID)
            post_file.write(posting)

            # Pack count into a byte array of size 4
            posting = struct.pack('I', count)
            post_file.write(posting)

        # Write to dictionary file and update byte offset
        dict_file.write(term + " " + str(df) + " " + str(byte_offset) + "\n")
        byte_offset += BYTE_SIZE * df * 2

    # Close files
    dict_file.close()
    post_file.close()

    return docs

"""
Checks if the token is a number
param:
    token:  token string
"""
def is_number(token):
    token = token.replace(",", "")
    try:
        float(token)
        return True
    except ValueError:
        return False
