from logic_operators import operator_chain  #imports a utility function to process logical rules for chaining

#chain parser for forward and backward chaining
def parse_chain_file(filename, method):
    knowledge_base = {}  #dictionary to store logical rules
    fact_set = set()  #set to store known facts
    query_statement = 0  #placeholder for the query statement
    parse_mode = 0  #keeps track of whether parsing "TELL" or "ASK" section

    #read the input file line by line
    with open(filename, 'r') as file:
        lines = file.read().splitlines()

    for line in lines:
        line = line.strip()  #remove leading and trailing whitespace
        if not line:
            continue  #skip empty lines

        if line == "TELL":
            #enter the tell section (knowledge base rules)
            parse_mode = 'TELL'

        elif line == "ASK":
            #enter the ask section (query statement)
            parse_mode = 'ASK'

        elif parse_mode == 'TELL':
            #parse logical rules in the tell section
            clauses = line.split(';')  #split rules by semicolons
            for clause in clauses:
                clause = clause.strip()  #remove extra whitespace
                #process the clause using the operator_chain function
                operator_chain(clause, method, knowledge_base, fact_set)

        elif parse_mode == 'ASK' and line:
            #parse the ask section (query statement)
            query_statement = line.strip()

    #return the parsed knowledge base, facts, and query statement
    return knowledge_base, fact_set, query_statement

#forward chaining
def forward_chaining(knowledge_base, fact_set, query_statement):
    changed = True  # Flag to track if new facts are being derived
    while changed:
        changed = False
        for condition, result in knowledge_base.items():
            if all(c in fact_set for c in condition):
                if result not in fact_set:
                    fact_set.add(result)
                    changed = True

    fact_set.discard('')  # Clean up any empty strings
    if query_statement in fact_set:
        derived_facts_list = sorted(fact_set, key=lambda x: (len(x), x))
        return f"> YES: " + ', '.join(derived_facts_list)
    else:
        return "NO"  # Print NO only if the query is not satisfied for valid Horn clauses
