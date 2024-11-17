import re 
from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple

class LogicalOperator(Enum):
    #enumeration of logical operators
    AND = auto()
    OR = auto()
    NOT = auto()
    IMPLIES = auto()
    IMPLIED_BY = auto()
    EQUIVALENCE = auto()

@dataclass
class ParsedExpression:
    #dataclass to hold parsed logical expression components
    left_side: Tuple[str, ...]
    right_side: str
    operator_type: LogicalOperator
    level: int = 0

class LogicParser:
    #parser for logical expressions with stadardized operator handinling
    OPERATOR_MAPPING = {
        '^': '&', '∧': '&',              # AND operators
        '|': '||',                       # OR operator
        '¬': '~', '!': '~',              # NOT operators
        '->': '=>', '→': '=>',           # IMPLIES operators
        '<-': '<=', '←': '<=',           # IMPLIED BY operators
        '<=>': '<->', '↔': '<->',        # EQUIVALENCE operators
    }

    #internal symbols to operator type mapping
    SYMBOL_TO_TYPE = {
        '&': LogicalOperator.AND,
        '||': LogicalOperator.OR,
        '~': LogicalOperator.NOT,
        '=>': LogicalOperator.IMPLIES,
        '<=': LogicalOperator.IMPLIED_BY,
        '<->': LogicalOperator.EQUIVALENCE
    }

    @classmethod
    def standardize_expression(cls, expression):
        #convert universal operators into internal symbols
        result = expression.strip()
        for universal, internal in cls.OPERATOR_MAPPING.items():
            result = result.replace(universal, internal)
        return result

    @classmethod
    def parse_expression(cls, expression, level: int = 0):
        #parse a logical expression into its components
        expression = cls.standardize_expression(expression)
        
        #handle simple facts
        if not any(symbol in expression for symbol in cls.SYMBOL_TO_TYPE.keys()):
            return expression

        #handle implications
        for symbol, op_type in cls.SYMBOL_TO_TYPE.items():
            if symbol in expression:
                parts = expression.split(symbol, 1)
                
                if op_type in {LogicalOperator.IMPLIES, LogicalOperator.IMPLIED_BY, LogicalOperator.EQUIVALENCE}:
                    left, right = parts if op_type != LogicalOperator.IMPLIED_BY else (parts[1], parts[0])
                    
                    #handle AND conditions
                    if '&' in left:
                        conditions = tuple(term.strip() for term in left.split('&'))
                        return ParsedExpression(conditions, right.strip(), op_type, level)
                    
                    #handle OR conditions
                    elif '||' in left:
                        conditions = tuple(f"*{term.strip()}" if term.strip() else term.strip() 
                                        for term in left.split('||'))
                        return ParsedExpression(conditions, right.strip(), op_type, level)
                    
                    #handle NOT conditions
                    elif '~' in left:
                        fact = left.strip('~').strip()
                        return ParsedExpression((fact,), "False", LogicalOperator.NOT, level)
                    
                    #handle simple implications
                    else:
                        return ParsedExpression((left.strip(),), right.strip(), op_type, level)

        return expression

#function to process logical operator table
def operator_table(expression, knowledge_base, facts_set):

    try: #parses the logical expression
        parsed = LogicParser.parse_expression(expression)
        
        #if parsed result is simple string (fact), add it to the facts set
        if isinstance(parsed, str):
            facts_set.add(parsed)
            facts_set.discard('') #remove empty strings
            return expression, facts_set
        
        if parsed.operator_type == LogicalOperator.EQUIVALENCE:
            #handle bi-directional implications
            knowledge_base.append((parsed.left_side, parsed.right_side)) #add forward implication to knowledge base
            reverse_sides = tuple(parsed.right_side.split('&')) #add the reverse implication to the knowledge base
            knowledge_base.append((reverse_sides, ' & '.join(parsed.left_side))) 
        else:
            knowledge_base.append((parsed.left_side, parsed.right_side)) #add a simple implication to the knowledge base
        
        return expression, facts_set
    except Exception as e: #handle errors during processing and log the details
        print(f"Error processing expression: {expression}")
        print(f"Error details: {str(e)}")
        return expression, facts_set

#function to process a chain of logical operators 
def operator_chain(expression, method, knowledge_base, facts_set):
    try:
        #early validation
        if any(char in expression for char in '()||~'):
            print("Generic KB is not applicable to FC and BC method.")
            return knowledge_base, facts_set

        #parse the logical expression 
        parsed = LogicParser.parse_expression(expression)
        
        #handle simple facts
        if isinstance(parsed, str):
            facts_set.add(parsed)
            return knowledge_base, facts_set

        #handle forward chaining 
        if method == "FC":
            knowledge_base[parsed.left_side] = parsed.right_side
            #add reverse implications for equivalence
            if parsed.operator_type == LogicalOperator.EQUIVALENCE:
                reverse_sides = tuple(parsed.right_side.split('&'))
                knowledge_base[reverse_sides] = ' & '.join(parsed.left_side)
        #handle backward chaining
        elif method == "BC":
            knowledge_base.setdefault(parsed.right_side, []).append(parsed.left_side)
            if parsed.operator_type == LogicalOperator.EQUIVALENCE:
                reverse_sides = tuple(parsed.right_side.split('&'))
                knowledge_base.setdefault(' & '.join(parsed.left_side), []).append(reverse_sides)

        return knowledge_base, facts_set
    except Exception as e:
        #handle errors during processing and log the details
        print(f"Error processing expression: {expression}")
        print(f"Error details: {str(e)}")
        return knowledge_base, facts_set

#function to handle generic operator table
def generic_operator_table(expression, knowledge_base, facts_set, level: int = 0):

    try:
        #increase the nesting level if the parentheses are detected
        if '(' in expression:
            level += 1
            #while there are parentheses in the expression
            while '(' in expression:
                #find all innermost parenthitical expressions
                inner_expressions = re.findall(r'\(([^()]+)\)', expression)
                for inner_expr in inner_expressions:
                    #recursively process each inner expression
                    generic_operator_table(inner_expr, knowledge_base, facts_set, level)
                #replace processed inner expressions with placeholds (@)
                expression = re.sub(r'\(([^()]+)\)', '@', expression)

        #parse the simplified expression
        parsed = LogicParser.parse_expression(expression, level)
        
        #handle simple facts
        if isinstance(parsed, str):
            facts_set.add(parsed)
            facts_set.discard('') #remove empty strings 
            return

        #handle equivalence (bi-directional implications)
        if parsed.operator_type == LogicalOperator.EQUIVALENCE:
            #add forward implication to the knowledge base 
            knowledge_base.append((parsed.left_side, parsed.right_side, level))
            #add reverse implication to the knowledge base 
            reverse_sides = tuple(parsed.right_side.split('&'))
            knowledge_base.append((reverse_sides, ' & '.join(parsed.left_side), level))
        else:
            #add simple implication to the knowledge base
            knowledge_base.append((parsed.left_side, parsed.right_side, level))
            
    except Exception as e:
        #handle errors during processing and log the details
        print(f"Error processing expression: {expression}")
        print(f"Error details: {str(e)}")