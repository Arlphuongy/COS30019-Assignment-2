import sys
from truth_table import parse_truth_table_file, evaluate_truth_table, evaluate_generic_truth_table
from forward_chaining import parse_chain_file, forward_chaining
from backward_chaining import parse_chain_file, backward_chaining

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
        print("Invalid search method")
        sys.exit(1)
