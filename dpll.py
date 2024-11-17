from logic_operators import LogicParser, LogicalOperator

class Literal:
    def __init__(self, name, negated = False):
        self.name = name
        self.negated = negated
    
    def __str__(self):
        return f"{'~' if self.negated else ''}{self.name}"
    
    def __eq__(self, other):
        if not isinstance(other, Literal):
            return False
        return self.name == other.name and self.negated == other.negated
    
    def __hash__(self):
        return hash((self.name, self.negated))
    
    def negate(self):
        return Literal(self.name, not self.negated)

class Clause:
    def __init__(self, literals):
        self.literals = set(literals)
    
    def __str__(self):
        return " ∨ ".join(str(lit) for lit in self.literals)
    
    def evaluate(self, assignment):
        if not all(lit.name in assignment for lit in self.literals):
            return None
        return any(
            (not lit.negated and assignment[lit.name]) or
            (lit.negated and not assignment[lit.name])
            for lit in self.literals
        )

class KnowledgeBase:
    def __init__(self):
        self.clauses = []
        self.symbols = set()
    
    def add_clause(self, clause: Clause):
        self.clauses.append(clause)
        for literal in clause.literals:
            self.symbols.add(literal.name)

def parse_knowledge_base(filename):
    kb = KnowledgeBase()
    
    with open(filename, 'r') as file:
        lines = file.read().split('\n')
    
    tell_content = []
    ask_query = ""
    parse_mode = None
    
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
    
    for expr in tell_content:
        parsed = LogicParser.parse_expression(expr)
        
        if isinstance(parsed, str):
            if parsed.startswith('~'):
                kb.add_clause(Clause([Literal(parsed[1:], True)]))
            else:
                kb.add_clause(Clause([Literal(parsed)]))
            continue
            
        if parsed.operator_type == LogicalOperator.IMPLIES:
            if len(parsed.left_side) == 1:
                kb.add_clause(Clause([Literal(parsed.left_side[0], True), Literal(parsed.right_side)]))
            else:
                literals = [Literal(ant, True) for ant in parsed.left_side]
                literals.append(Literal(parsed.right_side))
                kb.add_clause(Clause(literals))
                
        elif parsed.operator_type == LogicalOperator.EQUIVALENCE:
            kb.add_clause(Clause([Literal(parsed.left_side[0], True), Literal(parsed.right_side)]))
            kb.add_clause(Clause([Literal(parsed.right_side, True), Literal(parsed.left_side[0])]))
            
        elif parsed.operator_type == LogicalOperator.OR:
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

def find_pure_literal(kb, assignment):
    polarity = {}
    for clause in kb.clauses:
        for lit in clause.literals:
            if lit.name not in assignment:
                if lit.name not in polarity:
                    polarity[lit.name] = set()
                polarity[lit.name].add(lit.negated)
    
    for var, pols in polarity.items():
        if len(pols) == 1:
            return var, not list(pols)[0]
    return None

def find_unit_clause(kb, assignment):
    for clause in kb.clauses:
        unassigned = []
        is_satisfied = False
        
        for lit in clause.literals:
            if lit.name in assignment:
                if (not lit.negated and assignment[lit.name]) or (lit.negated and not assignment[lit.name]):
                    is_satisfied = True
                    break
            else:
                unassigned.append(lit)
        
        if not is_satisfied and len(unassigned) == 1:
            return unassigned[0].name, not unassigned[0].negated
    
    return None

def dpll_satisfiable(kb, assignment):
    if assignment is None:
        assignment = {}
    
    all_satisfied = True
    for clause in kb.clauses:
        result = clause.evaluate(assignment)
        if result is False:
            return None
        if result is None:
            all_satisfied = False
    
    if all_satisfied:
        return assignment
    
    unit = find_unit_clause(kb, assignment)
    if unit:
        var, value = unit
        new_assignment = assignment.copy()
        new_assignment[var] = value
        return dpll_satisfiable(kb, new_assignment)
    
    pure = find_pure_literal(kb, assignment)
    if pure:
        var, value = pure
        new_assignment = assignment.copy()
        new_assignment[var] = value
        return dpll_satisfiable(kb, new_assignment)
    
    var = next(iter(kb.symbols - set(assignment.keys())))
    
    assignment_true = assignment.copy()
    assignment_true[var] = True
    result = dpll_satisfiable(kb, assignment_true)
    if result is not None:
        return result
    
    assignment_false = assignment.copy()
    assignment_false[var] = False
    return dpll_satisfiable(kb, assignment_false)

def process_dpll_file(filename: str) -> bool:
    try:
        kb, query = parse_knowledge_base(filename)
        
        query_kb = KnowledgeBase()
        query_kb.clauses = kb.clauses.copy()
        query_kb.symbols = kb.symbols.copy()
        
        if query.startswith('~'):
            query_kb.add_clause(Clause([Literal(query[1:])]))
        else:
            query_kb.add_clause(Clause([Literal(query, True)]))
        
        return dpll_satisfiable(query_kb) is None
        
    except Exception as e:
        raise Exception(f"Error processing DPLL file: {str(e)}")