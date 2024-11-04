from itertools import chain
import re

def read(filename):
    """
    Reads and parse a knowledge base file which contains tell and ask statements
    Arguments:
        filename: path to the knowledge base file
    Returns:
        - List of tell statements
        - Query string (ask statement)
    """
    with open(filename) as f:
        lines = [line.strip().lower().split(';') for line in f]

    lines = [[item.strip() for item in line if item.strip()] for line in lines]
    #use itertools.chain to flatten lines
    flattened_lines = list(chain.from_iterable(lines))

    #seperates tell statemnets from query based on the 'ask' keyword
    try: 
        query_index = flattened_lines.index("ask")
    except ValueError:
        query_index = len(flattened_lines)
    
    #process tell statements
    tell = []
    for statement in flattened_lines[:query_index]:
        if statement.lower() not in ["", "tell", "ask"]:
            tell.append(statement)
    
    #process query
    query = ""
    if query_index + 1 < len(flattened_lines):
        query = flattened_lines[query_index + 1]

    return tell, query


def extract(tell):
    """
    Extracts symbols and sentences from tell statements
    Arguments:
        tell: the list of tell statments
    Returns:
        - Set of symbols 
        - List of processed sentences
    """
    symbols = set()
    sentences = []

    #regex pattern for symbol matching 
    symbol_pattern = r'\b[a-zA-Z][a-zA-Z0-9_]*\b'

    for sentence in tell:
        #finds all the symbols in the sentence
        found_symbols = re.findall(symbol_pattern, sentence)
        symbols.update(found_symbols)

        #stores the processed sentence
        sentences.append(sentence)
    
    return symbols, sentences

def validate_kb(tell, query):
    """
    Validates the knowledge base format and content
    Arguments:
        - tell: the list of tell statements
        - query: the query string
    Returns:
        bool: true if valid, false otherwise
    """
    if not tell and not query:
        return False
    
    for statement in tell:
        if not statement.strip():
            return False
    
    if query and not query.strip():
        return False
    
    return True

    
