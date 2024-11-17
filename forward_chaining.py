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
    changed = True  #flag to track if new facts are being derived
    while changed:
        changed = False  #reset the flag
        #iterate through the knowledge base rules
        for condition, result in knowledge_base.items():
            #check if all conditions for the rule are satisfied by the current facts
            if all(c in fact_set for c in condition):
                #add the resulting fact if it's not already known
                if result not in fact_set:
                    fact_set.add(result)
                    changed = True  #indicate that new facts were derived

    #remove any empty strings from the fact set
    fact_set.discard('')

    #sort the derived facts for consistent output
    derived_facts_list = sorted(fact_set, key=lambda x: (len(x), x))

    #check if the query is satisfied and return the result
    return f"> YES: " + ', '.join(derived_facts_list) if query_statement in fact_set else "NO"
