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

def operator_table(expression, knowledge_base, facts_set):

    try:
        parsed = LogicParser.parse_expression(expression)
        
        if isinstance(parsed, str):
            facts_set.add(parsed)
            facts_set.discard('')
            return expression, facts_set
        
        if parsed.operator_type == LogicalOperator.EQUIVALENCE:
            #handle bi-directional implications
            knowledge_base.append((parsed.left_side, parsed.right_side))
            reverse_sides = tuple(parsed.right_side.split('&'))
            knowledge_base.append((reverse_sides, ' & '.join(parsed.left_side)))
        else:
            knowledge_base.append((parsed.left_side, parsed.right_side))
        
        return expression, facts_set
    except Exception as e:
        print(f"Error processing expression: {expression}")
        print(f"Error details: {str(e)}")
        return expression, facts_set

def operator_chain(expression, method, knowledge_base, facts_set):

    try:
        #early validation
        if any(char in expression for char in '()||~'):
            print("Generic KB is not applicable to FC and BC method.")
            return knowledge_base, facts_set

        parsed = LogicParser.parse_expression(expression)
        
        if isinstance(parsed, str):
            facts_set.add(parsed)
            return knowledge_base, facts_set

        if method == "FC":
            knowledge_base[parsed.left_side] = parsed.right_side
            if parsed.operator_type == LogicalOperator.EQUIVALENCE:
                reverse_sides = tuple(parsed.right_side.split('&'))
                knowledge_base[reverse_sides] = ' & '.join(parsed.left_side)
        elif method == "BC":
            knowledge_base.setdefault(parsed.right_side, []).append(parsed.left_side)
            if parsed.operator_type == LogicalOperator.EQUIVALENCE:
                reverse_sides = tuple(parsed.right_side.split('&'))
                knowledge_base.setdefault(' & '.join(parsed.left_side), []).append(reverse_sides)

        return knowledge_base, facts_set
    except Exception as e:
        print(f"Error processing expression: {expression}")
        print(f"Error details: {str(e)}")
        return knowledge_base, facts_set

def generic_operator_table(expression, knowledge_base, facts_set, level: int = 0):

    try:
        if '(' in expression:
            level += 1
            while '(' in expression:
                inner_expressions = re.findall(r'\(([^()]+)\)', expression)
                for inner_expr in inner_expressions:
                    generic_operator_table(inner_expr, knowledge_base, facts_set, level)
                expression = re.sub(r'\(([^()]+)\)', '@', expression)

        parsed = LogicParser.parse_expression(expression, level)
        
        if isinstance(parsed, str):
            facts_set.add(parsed)
            facts_set.discard('')
            return

        if parsed.operator_type == LogicalOperator.EQUIVALENCE:
            knowledge_base.append((parsed.left_side, parsed.right_side, level))
            reverse_sides = tuple(parsed.right_side.split('&'))
            knowledge_base.append((reverse_sides, ' & '.join(parsed.left_side), level))
        else:
            knowledge_base.append((parsed.left_side, parsed.right_side, level))
            
    except Exception as e:
        print(f"Error processing expression: {expression}")
        print(f"Error details: {str(e)}")