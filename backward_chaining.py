from logic_operators import operator_chain  #immports a utility function to handle operator chains

def parse_chain_file(filename, method):
    knowledge_base = {}  #dictionary to hold logical rules for chaining
    fact_set = set()  #set to store known facts
    query_statement = 0  #placeholder for the query statement
    parse_mode = 0  #keps track of whether parsing "TELL" or "ASK" section

    #read and split the input file into lines
    with open(filename, 'r') as file:
        lines = file.read().splitlines()

    for line in lines:
        line = line.strip()  #remove leading and trailing whitespace
        if not line:
            continue  #skip empty lines

        if line == "TELL":
            #enter the TELL section (knowledge base rules)
            parse_mode = 'TELL'
        elif line == "ASK":
            #enter the ASK section (query)
            parse_mode = 'ASK'
        elif parse_mode == 'TELL':
            #parse and process logical rules in the TELL section
            clauses = line.split(';')  # Split multiple rules by semicolons
            for clause in clauses:
                clause = clause.strip()
                #process each clause using the operator_chain function
                operator_chain(clause, method, knowledge_base, fact_set)
        elif parse_mode == 'ASK' and line:
            #parse the ASK section (query statement)
            query_statement = line.strip()

    #return the parsed knowledge base, facts, and query statement
    return knowledge_base, fact_set, query_statement

#backward chaining
def backward_chaining(knowledge_base, fact_set, query_statement, derived_facts):
    #if the query is already a known fact, return success
    if query_statement in fact_set:
        derived_facts.add(query_statement)
        return True
    
    #if the query has no rules in the knowledge base, it cannot be satisfied
    if query_statement not in knowledge_base:
        return False

    #evaluate all conditions in the rules for the query
    for conditions in knowledge_base[query_statement]:
        #recursively check all conditions using backward chaining
        if all(backward_chaining(knowledge_base, fact_set, cond, derived_facts) for cond in conditions):
            #if all conditions are satisfied, the query is satisfied
            derived_facts.add(query_statement)
            #format the derived facts in sorted order for the result
            derived_facts_list = sorted(derived_facts, key=lambda x: (len(x), x))
            return "> YES: " + ', '.join(derived_facts_list)
        else:
            #if any condition fails, the query cannot be satisfied
            return "NO"
    return False
