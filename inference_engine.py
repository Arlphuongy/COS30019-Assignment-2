import sys
from itertools import product
from logic_operators import operator_table, operator_chain, generic_operator_table

# TRUTH TABLE PARSER
def parse_truth_table_file(filename):
    with open(filename, 'r') as file:
        lines = file.read().split('\n')
    knowledge_base = []
    fact_set = set()  # Set of facts from the KB
    query_statement = 0
    parse_mode = 0
    bracket_flag = 0  # 0 indicates no brackets in test case, 1 indicates brackets
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
                if any('(' in clause for clause in clauses):
                    bracket_flag = 1
                if bracket_flag == 0:
                    operator_table(clause, knowledge_base, fact_set)
                else:
                    generic_operator_table(clause, knowledge_base, fact_set)
        elif parse_mode == 'ASK' and line:
            query_statement = line.strip()
    return knowledge_base, fact_set, query_statement, bracket_flag

# Constructing truth table for symbols in KB
def generate_truth_combinations(symbols):
    num_symbols = len(symbols)
    truth_combinations = []
    for truth_values in product([True, False], repeat=num_symbols):
        truth_combinations.append(dict(zip(symbols, truth_values)))
    return truth_combinations

# Basic truth table evaluation without handling brackets
def evaluate_truth_table(knowledge_base, fact_set, query_statement):
    symbols = set()
    for condition, _ in knowledge_base:
        symbols.update(condition)
    symbols.update(fact_set)
    truth_combinations = generate_truth_combinations(symbols)
    for row in truth_combinations:
        for fact in fact_set:
            row[fact] = True
        for condition, result in knowledge_base:
            if any('*' in c for c in condition):
                condition = tuple(c.replace('*', '') for c in condition)
                if any(row.get(c, False) for c in condition):
                    row[result] = True
                condition = tuple(c for c in condition if c.strip())
            else:
                if all(row[c] for c in condition):
                    row[result] = True
    evaluated_clause = condition + (query_statement,)
    return f"> YES: {len(evaluated_clause)}" if query_statement in truth_combinations[-1] and truth_combinations[-1][query_statement] else "NO"

def evaluate_clause(row, condition):
    if isinstance(condition, tuple):
        return all(row.get(c, False) for c in condition)
    return row.get(condition, False)

# Truth table evaluation for expressions with brackets
def evaluate_generic_truth_table(knowledge_base, fact_set, query_statement):
    symbols = set()
    for condition, _, _ in knowledge_base:
        symbols.update(condition)
    symbols.update(fact_set)
    truth_combinations = generate_truth_combinations(symbols)

    bracketed_clauses = {}
    for clause in knowledge_base:
        if clause[2] not in bracketed_clauses:
            bracketed_clauses[clause[2]] = []
        bracketed_clauses[clause[2]].append(clause)

    for row in truth_combinations:
        for fact in fact_set:
            row[fact] = True

        for level in sorted(bracketed_clauses.keys()):
            level_results = {}
            for condition, result, _ in bracketed_clauses[level]:
                if condition == ('@',):
                    inner_conditions = []
                    for prev_level in range(level - 1, -1, -1):
                        for cond, res, _ in bracketed_clauses.get(prev_level, []):
                            if cond == ('@',):
                                inner_conditions.append(knowledge_base[0][0])
                            else:
                                inner_conditions.append(cond)
                    for inner_condition in inner_conditions:
                        if any('*' in c for c in condition):
                            condition = tuple(c.replace('*', '') for c in condition)
                            if any(row.get(c, False) for c in condition):
                                row[result] = True
                            condition = tuple(c for c in condition if c.strip())
                        else:
                            if evaluate_clause(row, inner_condition):
                                level_results[result] = True
                else:
                    if any('*' in c for c in condition):
                        condition = tuple(c.replace('*', '') for c in condition)
                        if any(row.get(c, False) for c in condition):
                            row[result] = True
                        condition = tuple(c for c in condition if c.strip())
                    else:
                        if evaluate_clause(row, condition):
                            level_results[result] = True
                    inner_condition = ()
            for result in level_results:
                row[result] = True
    evaluated_clause = len(condition) + len(bracketed_clauses) + len(query_statement) + len(inner_condition)
    return f"> YES {evaluated_clause}" if evaluate_clause(truth_combinations[-1], query_statement) else "NO"

# Chain parser for forward and backward chaining
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

# Main execution
if __name__ == "__main__":
    filename = sys.argv[1]
    method = sys.argv[2]

    if method == "TT":
        knowledge_base, fact_set, query_statement, bracket_flag = parse_truth_table_file(filename)
        if bracket_flag == 0:
            result = evaluate_truth_table(knowledge_base, fact_set, query_statement)
        elif bracket_flag == 1:
            result = evaluate_generic_truth_table(knowledge_base, fact_set, query_statement)
        print(result)

    elif method == "FC":
        knowledge_base, fact_set, query_statement = parse_chain_file(filename, method)
        result = forward_chaining(knowledge_base, fact_set, query_statement)
        print(result)

    elif method == "BC":
        knowledge_base, fact_set, query_statement = parse_chain_file(filename, method)
        derived_facts = set()
        result = backward_chaining(knowledge_base, fact_set, query_statement, derived_facts)
        print(result)

    else:
        print("Invalid search method. Please choose among: TT, FC, BC")
        sys.exit(1)
