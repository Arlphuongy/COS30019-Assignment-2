from itertools import product 
from logic_operators import operator_table, generic_operator_table 

#truth table parser
def parse_truth_table_file(filename):
    with open(filename, 'r') as file:
        lines = file.read().split('\n') #reads all lines and split by newline

    knowledge_base = [] #stores the logical statements from the knowledge base
    fact_set = set()  #set of facts from the KB
    query_statement = 0 #placeholder for the ask statement
    parse_mode = 0 #tracks whether currently parsing TELL or ASK
    bracket_flag = 0  # 0 indicates no brackets in test case, 1 indicates brackets

    for line in lines: 
        line = line.strip()
        if line == "TELL":
            parse_mode = 'TELL' #switch to parsing knowledge base (tell mode)
        elif line == "ASK":
            parse_mode = 'ASK' #switch to parsing query (ask mode)
        elif parse_mode == 'TELL':
            #parse logical statements from the tell section
            clauses = line.split(';') 
            for clause in clauses:
                clause = clause.strip()
                if any('(' in clause for clause in clauses):
                    #detect if any clause contains brackets
                    bracket_flag = 1
                if bracket_flag == 0:
                    #process clause without brackets using the basic operator table
                    operator_table(clause, knowledge_base, fact_set)
                else:
                    #process clause with brackets using the generic operator table
                    generic_operator_table(clause, knowledge_base, fact_set)
        elif parse_mode == 'ASK' and line:
            #parse the query 
            query_statement = line.strip()
    return knowledge_base, fact_set, query_statement, bracket_flag 

#constructing truth table for symbols in KB
def generate_truth_combinations(symbols):
    num_symbols = len(symbols) #determine number of symbols
    truth_combinations = []
    #generate cartesian product of truth values for all symbols
    for truth_values in product([True, False], repeat=num_symbols):
        #map each symbol to its corresponding truth value
        truth_combinations.append(dict(zip(symbols, truth_values)))
    return truth_combinations

def evaluate_clause(row, condition): #evaluates single logical clause given a row of truth values
    if isinstance(condition, tuple):
        return all(row.get(c, False) for c in condition)
    return row.get(condition, False)

#basic truth table evaluation without handling brackets
def evaluate_truth_table(knowledge_base, fact_set, query_statement):
    symbols = set()  # collect symbols from knowledge base and facts

    #add symbols from kb
    for condition, _ in knowledge_base:
        symbols.update(condition)

    symbols.update(fact_set)  #add symbols from facts
    truth_combinations = generate_truth_combinations(symbols)

    final_conditions = []  #store conditions for final evaluation
    
    for row in truth_combinations:  #evaluate each row in the truth table
        #set the known facts to true in current row
        for fact in fact_set:
            row[fact] = True
            
        for condition, result in knowledge_base:
            #store current condition for final evaluation
            final_conditions = condition
            
            #handle or conditions
            if any('*' in c for c in condition):
                clean_condition = tuple(c.replace('*', '') for c in condition)
                #if any condition is true, set result to true
                if any(row.get(c, False) for c in clean_condition):
                    row[result] = True
            else:
                #handle and conditions
                if all(row[c] for c in condition):
                    row[result] = True

    #combine the evaluated condition and query
    evaluated_clause = final_conditions + (query_statement,)
    #check if the query is true in final row
    return f"> YES: {len(evaluated_clause)}" if query_statement in truth_combinations[-1] and truth_combinations[-1][query_statement] else "NO"

def evaluate_generic_truth_table(knowledge_base, fact_set, query_statement):
    symbols = set()

    for condition, _, _ in knowledge_base:
        symbols.update(condition)

    symbols.update(fact_set)
    truth_combinations = generate_truth_combinations(symbols)

    #organize clauses by their nesting level
    bracketed_clauses = {}
    final_conditions = []
    
    for clause in knowledge_base:
        if clause[2] not in bracketed_clauses:
            bracketed_clauses[clause[2]] = []
        bracketed_clauses[clause[2]].append(clause)
        final_conditions = clause[0]  #store the last condition

    #evaluate each row in the truth table
    for row in truth_combinations:
        for fact in fact_set:  #set known facts to true
            row[fact] = True

        #evaluate clauses level by level
        for level in sorted(bracketed_clauses.keys()):
            level_results = {}
            for condition, result, _ in bracketed_clauses[level]:
                #handle inner conditions for nested clauses
                if condition == ('@',):
                    inner_conditions = []
                    for prev_level in range(level - 1, -1, -1):
                        for cond, res, _ in bracketed_clauses.get(prev_level, []):
                            if cond == ('@',):
                                inner_conditions.append(knowledge_base[0][0])
                            else:
                                inner_conditions.append(cond)
                    #evaluate inner conditions
                    for inner_condition in inner_conditions:
                        if evaluate_clause(row, inner_condition):
                            level_results[result] = True
                else:
                    #handle or conditions
                    if any('*' in c for c in condition):
                        clean_condition = tuple(c.replace('*', '') for c in condition)
                        if any(row.get(c, False) for c in clean_condition):
                            row[result] = True
                    else:
                        #evaluate the condition normally
                        if evaluate_clause(row, condition):
                            level_results[result] = True

            #set the results for the current level in the truth table row
            for result in level_results:
                row[result] = True

    #combine evaluated condition and query
    evaluated_clause = len(final_conditions) + len(bracketed_clauses) + len(query_statement)
    #return whether the query is satisfied in the final row
    return f"> YES {evaluated_clause}" if evaluate_clause(truth_combinations[-1], query_statement) else "NO"