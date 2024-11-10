from logic_operators import operator_chain

def parse_chain_file(filename, method):
    with open(filename, 'r') as file:
        lines = file.read().split('\n')
    knowledge_base = {}
    fact_set = set()
    query_statement = 0
    parse_mode = 0
    for line in lines:
        line = line.strip()
        if line == "TELL":
            parse_mode = 'TELL'
        elif line == "ASK":
            parse_mode = 'ASK'
        elif parse_mode == 'TELL':
            clauses = line.split(';')
            for clause in clauses:
                clause = clause.strip()
                operator_chain(clause, method, knowledge_base, fact_set)
        elif parse_mode == 'ASK' and line:
            query_statement = line.strip()
    return knowledge_base, fact_set, query_statement

# Backward chaining
def backward_chaining(knowledge_base, fact_set, query_statement, derived_facts):
    if query_statement in fact_set:
        derived_facts.add(query_statement)
        return True
    if query_statement not in knowledge_base:
        return False
    for conditions in knowledge_base[query_statement]:
        if all(backward_chaining(knowledge_base, fact_set, cond, derived_facts) for cond in conditions):
            derived_facts.add(query_statement)
            derived_facts_list = sorted(derived_facts, key=lambda x: (len(x), x))
            return "> YES: " + ', '.join(derived_facts_list)
        else:
            return "NO"
    return False
