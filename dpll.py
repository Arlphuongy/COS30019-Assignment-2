from logic_operators import LogicParser, LogicalOperator  # Import logical parsing utilities and operator enumeration

#represents a literal (atomic statement) in logical expressions
class Literal: #initialize a literal with a name and negation status
    def __init__(self, name, negated=False):
        self.name = name
        self.negated = negated

    def __str__(self): #string representation of literal
        return f"{'~' if self.negated else ''}{self.name}"

    def __eq__(self, other): #equality check for literals based on name and negation
        if not isinstance(other, Literal):
            return False
        return self.name == other.name and self.negated == other.negated

    def __hash__(self): #hash function to allow literals to be used in sets
        return hash((self.name, self.negated))

    def negate(self): #returns the negation of the current literal
        return Literal(self.name, not self.negated)

#represents a disjunction of literals
class Clause:
    def __init__(self, literals): #initialize a clause containing a set of literals
        self.literals = set(literals)

    def __str__(self): #string representation of the clause
        return " ∨ ".join(str(lit) for lit in self.literals)

    def evaluate(self, assignment): #evalautes the clause based on given asssignment
        if not all(lit.name in assignment for lit in self.literals):
            return None  # Undecided if some literals are unassigned
        return any(
            (not lit.negated and assignment[lit.name]) or
            (lit.negated and not assignment[lit.name])
            for lit in self.literals
        )

#represents a knowledge base composed of multiple clauses
class KnowledgeBase: #initialize an empty knowledge base with clauses and symbols
    def __init__(self):
        self.clauses = []  # List of clauses
        self.symbols = set()  # Set of unique symbols in the clauses

    def add_clause(self, clause: Clause): #adds a clause to the knowledge base and updates the symbol set
        self.clauses.append(clause)
        for literal in clause.literals:
            self.symbols.add(literal.name)

def parse_knowledge_base(filename): #parses a file to construct a knowledge base and a query statement
    kb = KnowledgeBase()  #create a new knowledge base

    with open(filename, 'r') as file:
        lines = file.read().split('\n')  #read all lines from the file

    tell_content = []  #stores rules from the TELL section
    ask_query = ""  #stores the ASK query
    parse_mode = None  #tracks whether parsing "tell" or "ask"

    for line in lines:
        line = line.strip()
        if line == "TELL":
            parse_mode = 'TELL'
        elif line == "ASK":
            parse_mode = 'ASK'
        elif parse_mode == 'TELL' and line:
            tell_content.extend(expr.strip() for expr in line.split(';') if expr.strip())
        elif parse_mode == 'ASK' and line:
            ask_query = line.strip()

    # Parse rules from the TELL section into the knowledge base
    for expr in tell_content:
        parsed = LogicParser.parse_expression(expr)

        if isinstance(parsed, str):
            if parsed.startswith('~'):
                kb.add_clause(Clause([Literal(parsed[1:], True)]))  # Add negated literal
            else:
                kb.add_clause(Clause([Literal(parsed)]))  # Add positive literal
            continue

        if parsed.operator_type == LogicalOperator.IMPLIES:
            # Add implication as a clause
            if len(parsed.left_side) == 1:
                kb.add_clause(Clause([Literal(parsed.left_side[0], True), Literal(parsed.right_side)]))
            else:
                literals = [Literal(ant, True) for ant in parsed.left_side]
                literals.append(Literal(parsed.right_side))
                kb.add_clause(Clause(literals))

        elif parsed.operator_type == LogicalOperator.EQUIVALENCE:
            # Add equivalence as two implications
            kb.add_clause(Clause([Literal(parsed.left_side[0], True), Literal(parsed.right_side)]))
            kb.add_clause(Clause([Literal(parsed.right_side, True), Literal(parsed.left_side[0])]))

        elif parsed.operator_type == LogicalOperator.OR:
            # Add disjunction of literals
            literals = []
            for term in parsed.left_side:
                if term.startswith('*'):
                    term = term[1:]
                if term.startswith('~'):
                    literals.append(Literal(term[1:], True))
                else:
                    literals.append(Literal(term))
            kb.add_clause(Clause(literals))

    return kb, ask_query
