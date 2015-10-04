#!/usr/bin/python
import re
import nltk
import sys
import getopt
import codecs
import struct
import math
import io
import collections
import timeit

# Size of the BYTE for storing the docID
BYTE_SIZE = 4

"""
Perform boolean queries from the submitted query and returns the result
params:
    dictionary_file:    dictionary file produced by indexer
    postings_file:      postings file produced by indexer
    query:              file of boolean queries
"""
def search(dictionary_file, postings_file, query):
    # Open files
    dict_file = codecs.open(dictionary_file, encoding='utf-8')
    post_file = io.open(postings_file, 'rb')

    # Load dictionary to memory
    loaded_dict = load_dictionary(dict_file)

    # Dictionary map of terms to tuple of document frequency and offset
    dictionary = loaded_dict[0]

    # List of all docIDs indexed in sorted order
    indexed_docIDs = loaded_dict[1]
    dict_file.close()

    # Process each query
    queries_list = str(query)

    result = process_query(queries_list, dictionary, post_file, indexed_docIDs)

    # Close files
    post_file.close()

    return result

"""
returns 2-tuple of loaded dictionary and total document frequency
params:
    dict_file: opened dictionary file
"""
def load_dictionary(dict_file):
    dictionary = {}
    indexed_docIDs = []
    docIDs_processed = False

    # Load each term along with its df and postings file pointer to dictionary
    for entry in dict_file.read().split('\n'):
        if (entry):
            if (not docIDs_processed):
                indexed_docIDs = [int(docID) for docID in entry[20:-1].split(',')]
                docIDs_processed = True
            else:
                token = entry.split(" ")
                term = token[0]
                df = int(token[1])
                offset = int(token[2])
                dictionary[term] = (df, offset)

    return (dictionary, indexed_docIDs)

"""
Process query and return the list of docIDs
params:
    query:          the query string
    dictionary:     the dictionary in memory
    indexed_docIDs: the list of all docIDs indexed (used for negations)

"""
def process_query(query, dictionary, post_file, indexed_docIDs):
    stemmer = nltk.stem.porter.PorterStemmer()

    query = query.replace('(', '( ')
    query = query.replace(')', ' )')
    query = query.split(' ')

    results_stack = []
    postfix_queue = collections.deque(shunting_yard(query))

    while postfix_queue:
        token = postfix_queue.popleft()
        result = []

        if (token != 'AND' and token != 'OR' and token != 'NOT'):
            token = stemmer.stem(token)
            if (token in dictionary):
                result = load_posting_list(post_file, dictionary[token][0], dictionary[token][1])
        elif (token == 'AND'):
            right_operand = results_stack.pop()
            left_operand = results_stack.pop()
            result = boolean_AND(left_operand, right_operand)
        elif (token == 'OR'):
            right_operand = results_stack.pop()
            left_operand = results_stack.pop()
            result = boolean_OR(left_operand, right_operand)
        elif (token == 'NOT'):
            right_operand = results_stack.pop()
            result = boolean_NOT(right_operand, indexed_docIDs)

        results_stack.append(result)

    if len(results_stack) != 1:
        print ("ERROR: results_stack. Please check valid query")

    return results_stack.pop()

"""
returns posting list for term corresponding to the given offset
params:
    post_file:  opened postings file
    length:     length of posting list
    offset:     byte offset which acts as pointer to start of posting list in postings file
"""
def load_posting_list(post_file, length, offset):
    post_file.seek(offset)
    posting_list = []
    for i in range(length):
        # Read the docID
        posting = post_file.read(BYTE_SIZE)
        docID = struct.unpack('I', posting)[0]

        # Read the count
        posting = post_file.read(BYTE_SIZE)
        count = struct.unpack('I', posting)[0]

        posting_list.append((docID, count))
    return posting_list

"""
returns the list of postfix tokens converted from the given infix expression
params:
    infix_tokens: list of tokens in original query of infix notation
"""
def shunting_yard(infix_tokens):
    precedence = {}
    precedence['NOT'] = 3
    precedence['AND'] = 2
    precedence['OR'] = 1
    precedence['('] = 0
    precedence[')'] = 0

    output = []
    operator_stack = []

    for token in infix_tokens:

        if (token == '('):
            operator_stack.append(token)
        elif (token == ')'):
            operator = operator_stack.pop()
            while operator != '(':
                output.append(operator)
                operator = operator_stack.pop()
        elif (token in precedence):
            if (operator_stack):
                current_operator = operator_stack[-1]
                while (operator_stack and precedence[current_operator] > precedence[token]):
                    output.append(operator_stack.pop())
                    if (operator_stack):
                        current_operator = operator_stack[-1]

            operator_stack.append(token)
        else:
            output.append(token.lower())

    while (operator_stack):
        output.append(operator_stack.pop())
    return output

"""
returns the list of docIDs which is the compliment of given right_operand
params:
    right_operand:  sorted list of docIDs to be complimented
    indexed_docIDs: sorted list of all docIDs indexed
"""
def boolean_NOT(right_operand, indexed_docIDs):
    if (not right_operand):
        return [(id, 0) for id in indexed_docIDs]

    result = []
    r_index = 0
    for item in indexed_docIDs:
        if (item != right_operand[r_index][0]):
            result.append((item, 0))
        elif (r_index + 1 < len(right_operand)):
            r_index += 1
    return result

"""
returns list of docIDs that results from 'OR' operation between left and right operands
params:
    left_operand:   docID list on the left
    right_operand:  docID list on the right
"""
def boolean_OR(left_operand, right_operand):
    result = []
    l_index = 0
    r_index = 0

    while (l_index < len(left_operand) or r_index < len(right_operand)):
        if (l_index < len(left_operand) and r_index < len(right_operand)):
            l_item = left_operand[l_index]
            r_item = right_operand[r_index]

            if (l_item == r_item):
                result.append(l_item)
                l_index += 1
                r_index += 1
            elif (l_item > r_item):
                result.append(r_item)
                r_index += 1
            else:
                result.append(l_item)
                l_index += 1
        elif (l_index >= len(left_operand)):
            r_item = right_operand[r_index]
            result.append(r_item)
            r_index += 1
        else:
            l_item = left_operand[l_index]
            result.append(l_item)
            l_index += 1

    return result

"""
returns list of docIDs that results from 'AND' operation between left and right operands
params:
    left_operand:   docID list on the left
    right_operand:  docID list on the right
"""
def boolean_AND(left_operand, right_operand):
    result = []
    l_index = 0
    r_index = 0
    l_skip = int(math.sqrt(len(left_operand)))
    r_skip = int(math.sqrt(len(right_operand)))

    while (l_index < len(left_operand) and r_index < len(right_operand)):
        l_item = left_operand[l_index]
        r_item = right_operand[r_index]

        if (l_item == r_item):
            result.append(l_item)
            l_index += 1
            r_index += 1
        elif (l_item > r_item):
            if (r_index + r_skip < len(right_operand)) and right_operand[r_index + r_skip] <= l_item:
                r_index += r_skip
            else:
                r_index += 1
        else:
            if (l_index + l_skip < len(left_operand)) and left_operand[l_index + l_skip] <= r_item:
                l_index += l_skip
            else:
                l_index += 1

    return result