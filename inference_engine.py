import re
import sys
from itertools import product  # For generating all possible truth assignments
from logic_operators import operator_table, operator_chain, generic_operator_table

# Function to parse the input file and return the knowledge base (kb) and the query
def parse_file(filename):
    """Reads the input file and extracts the knowledge base and query."""
    with open(filename, 'r') as file:
        lines = file.read().strip().splitlines()  # Read and split file by lines
    
    kb = []  # Knowledge base will be stored here
    query = None  # This will store the query to be answered
    tell_mode = False  # Flag to indicate if we are reading facts (TELL mode)
    ask_mode = False  # Flag to indicate if we are reading a query (ASK mode)
    
    for line in lines:
        line = line.strip()  # Clean up any leading or trailing whitespace
        if line == "TELL":
            tell_mode = True  # Start reading facts (knowledge base)
            ask_mode = False
        elif line == "ASK":
            ask_mode = True  # Start reading the query
            tell_mode = False
        elif tell_mode:
            kb = line.split(';')  # Split the Horn clauses by ';'
        elif ask_mode:
            query = line.strip()  # Store the query when in ASK mode
    
    return kb, query

# Function to check entailment using the Truth Table method (TT)
def TT_entails(kb, query):
    """Check if the knowledge base entails the query using a truth table."""
    facts = set()  # Facts extracted from the knowledge base
    processed_kb = []  # Processed knowledge base to handle logical operators

    # Process each clause in the knowledge base using a helper function
    for clause in kb:
        generic_operator_table(clause.strip(), processed_kb, facts)

    # Extract all unique propositional symbols from the knowledge base and query
    symbols = extract_symbols(kb + [query])

    # Generate all possible truth assignments (models) for the symbols
    models = list(product([False, True], repeat=len(symbols)))
    num_models = 0  # Counter for how many models satisfy the query

    # Check each model to see if it satisfies the knowledge base and the query
    for model in models:
        model_dict = {symbols[i]: model[i] for i in range(len(symbols))}
        if all(evaluate_clause(clause, model_dict) for clause in processed_kb):
            if evaluate_clause(query, model_dict):
                num_models += 1  # If the model satisfies the query, increment the count

    return num_models > 0, num_models  # Return True if query is entailed, and the count of such models

# Function to extract all unique symbols (propositional variables) from the KB and query
def extract_symbols(kb):
    """Extract all unique propositional symbols from the knowledge base and query."""
    symbols = set()  # Set to store symbols
    for clause in kb:
        # Remove logical operators to extract the symbols
        clause = re.sub(r'[&|()~=><]', ' ', clause)
        for symbol in clause.split():
            if symbol and not symbol.isdigit():
                symbols.add(symbol)  # Add the symbol to the set
    return sorted(symbols)  # Return sorted list of unique symbols

# Function to evaluate a logical clause under a specific truth assignment (model)
def evaluate_clause(clause, model):
    """Evaluate a clause (logical expression) using a given truth model."""
    # Replace each symbol in the clause with its corresponding value from the model
    for symbol, value in model.items():
        clause = clause.replace(symbol, str(value))
    
    # Handle implication by converting '=>' to 'or not' (standard logical equivalence)
    clause = clause.replace('=>', ' or not ')  # Implication handling
    return eval(clause)  # Evaluate the clause as a Python expression

# Forward Chaining Inference method
def forward_chain(kb, query):
    """Perform forward chaining to try to infer the query from the knowledge base."""
    facts = set()  # Facts that are known to be true
    kb_dict = {}  # Dictionary to store rules in KB (premise -> conclusion)

    # Process each clause in the knowledge base using operator_chain function
    for clause in kb:
        operator_chain(clause.strip(), "FC", kb_dict, facts)

    agenda = list(facts)  # Initialize agenda with known facts
    inferred = set()  # Set to track inferred facts

    # Process each fact in the agenda
    while agenda:
        p = agenda.pop(0)  # Get the first fact from the agenda
        if p == query:
            return True, inferred.union({p})  # If we inferred the query, return True
        if p not in inferred:
            inferred.add(p)  # Mark the fact as inferred
            # Check if any rule can be applied using this fact
            for condition, conclusion in kb_dict.items():
                if all(symbol in inferred for symbol in condition):
                    agenda.append(conclusion)  # Add the conclusion to the agenda if the condition is satisfied
    
    return False, inferred  # Return False if query is not inferred

# Backward Chaining Inference method
def backward_chain(kb, query):
    """Perform backward chaining to try to prove the query from the knowledge base."""
    facts = set()  # Set of known facts
    kb_dict = {}  # Dictionary to store rules (goal -> conditions)

    # Process each clause in the knowledge base using operator_chain function
    for clause in kb:
        operator_chain(clause.strip(), "BC", kb_dict, facts)

    # Start the backward chaining process
    return BC_or(kb_dict, query, set())

# Recursive function for OR in backward chaining (checking if goal can be proved)
def BC_or(kb_dict, goal, inferred):
    """Recursive OR for backward chaining (if the goal can be proved)."""
    if goal in inferred:
        return True  # If the goal is already inferred, return True
    inferred.add(goal)  # Mark goal as inferred
    if goal in kb_dict:
        # Check if we can infer the goal by examining its premises
        for premise in kb_dict[goal]:
            if BC_and(kb_dict, premise, inferred):
                return True  # If any premise leads to the goal, return True
    return False  # Return False if goal can't be proved

# Recursive function for AND in backward chaining (check all premises)
def BC_and(kb_dict, premises, inferred):
    """Recursive AND for backward chaining (check all premises of a rule)."""
    for premise in premises:
        if not BC_or(kb_dict, premise, inferred):
            return False  # If any premise can't be proved, return False
    return True  # All premises are proved, so return True

# Main function to run the inference engine
def iengine(filename, method):
    """Main function to run the inference engine based on the selected method."""
    kb, query = parse_file(filename)  # Parse the knowledge base and query from the input file

    # Run the appropriate inference method based on the user's choice
    if method == "TT":
        entailed, num_models = TT_entails(kb, query)
        if entailed:
            print(f"YES: {num_models}")  # Query is entailed by the KB, print number of models
        else:
            print("NO")  # Query is not entailed by the KB
    elif method == "FC":
        entailed, inferred = forward_chain(kb, query)
        if entailed:
            print(f"YES: {', '.join(inferred)}")  # Print all inferred facts that lead to the query
        else:
            print("NO")  # Query can't be inferred from the KB
    elif method == "BC":
        entailed = backward_chain(kb, query)
        if entailed:
            print(f"YES: {query}")  # Query can be proved using backward chaining
        else:
            print("NO")  # Query can't be proved using backward chaining
    else:
        print("Invalid method! Use TT, FC, or BC.")  # Handle invalid method input

# Entry point of the program
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python iengine.py <filename> <method>")
    else:
        filename = sys.argv[1]  # Get the input filename from the command line arguments
        method = sys.argv[2]  # Get the inference method from the command line arguments
        iengine(filename, method)  # Run the inference engine with the specified method
