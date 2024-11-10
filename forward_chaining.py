from logic_operators import operator_chain

# Chain parser for forward and backward chaining
def parse_chain_file(filename, method):
    knowledge_base = {}
    fact_set = set()
    query_statement = 0
    parse_mode = 0
    with open(filename, 'r') as file:
        lines = file.read().splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

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

# Forward chaining
def forward_chaining(knowledge_base, fact_set, query_statement):
    changed = True
    while changed:
        changed = False
        for condition, result in knowledge_base.items():
            if all(c in fact_set for c in condition):
                if result not in fact_set:
                    fact_set.add(result)
                    changed = True
    fact_set.discard('')
    derived_facts_list = sorted(fact_set, key=lambda x: (len(x), x))
    return f"> YES: " + ', '.join(derived_facts_list) if query_statement in fact_set else "NO"
