import re
from itertools import product

# Mapping of universal logical operators to internal symbols
operator_mapping = {
    '^': '&', '∧': '&',
    '|': '||',
    '¬': '~', '!': '~',
    '->': '=>', '→': '=>',
    '<-': '<=', '←': '<=',
    '<=>': '<->', '↔': '<->',
}

def operator_table(expression, knowledge_base, facts_set):
    # Replacing universal operators with internal symbols
    for variable, symbol in operator_mapping.items():
        expression = expression.replace(variable, symbol)
    
    if '=>' in expression:
        parts = expression.split('=>')
        if '&' in parts[0]:
            left_side = tuple([term.strip() for term in parts[0].split('&')])
            right_side = parts[1].strip()
            knowledge_base.append((left_side, right_side))
        elif '||' in parts[0]:
            left_side = tuple(['*' + term.strip() if term.strip() else term.strip() for term in parts[0].split('||')])
            right_side = parts[1].strip()
            knowledge_base.append((left_side, right_side))
        elif '~' in parts[0]:
            fact = parts[0].strip('~').strip()
            if fact:
                knowledge_base.append((fact, False))
        else:
            left_side = tuple(term.strip() for term in parts[0].split('=>'))
            right_side = parts[1].strip()
            knowledge_base.append((left_side, right_side))
    elif '<=' in expression:
        parts = expression.split('<=')
        if '&' in parts[1]:
            right_side = tuple([term.strip() for term in parts[1].split('&')])
            left_side = parts[0].strip()
            knowledge_base.append((right_side, left_side))
        elif '||' in parts[1]:
            right_side = tuple(['*' + term.strip() if term.strip() else term.strip() for term in parts[1].split('||')])
            left_side = parts[0].strip()
            knowledge_base.append((right_side, left_side))
        elif '~' in parts[1]:
            fact = parts[0].strip('~').strip()
            if fact:
                knowledge_base.append((fact, False))
        else:
            right_side = tuple(term.strip() for term in parts[1].split('<=')) 
            left_side = parts[0].strip()
            knowledge_base.append((right_side, left_side))
    elif '<->' in expression:
        if '&' in expression:
            parts = expression.split('<->')
            left_side = tuple([term.strip() for term in parts[0].split('&')])
            right_side = parts[1].strip()
            knowledge_base.append((left_side, right_side))
            knowledge_base.append((tuple(right_side.split('&')), left_side))
        elif '||' in expression:
            parts = expression.split('<->')
            left_side = tuple(['*' + term.strip() if term.strip() else term.strip() for term in parts[0].split('||')])
            right_side = parts[1].strip()
            knowledge_base.append((left_side, right_side))
            knowledge_base.append((tuple(right_side.split('||')), left_side))
        elif '~' in expression:
            fact = expression.strip('~').strip()
            if fact:
                knowledge_base.append((fact, False))
        else:
            parts = expression.split('<->')
            left_side = tuple([term.strip() for term in parts[0].split('<->')])
            right_side = parts[1].strip()
            knowledge_base.append((left_side, right_side))
            knowledge_base.append((tuple(right_side.split('<->')), left_side))
    else:
        facts_set.add(expression)
        facts_set.discard('')
    
    return expression, facts_set 

def operator_chain(expression, method, knowledge_base, facts_set):
    for variable, symbol in operator_mapping.items():
        expression = expression.replace(variable, symbol)
    
    if '(' in expression or '||' in expression or '~' in expression:
        print("Generic KB is not applicable to FC and BC method.")
        return
    if '=>' in expression:
        left_side, right_side = expression.split('=>')
        left_parts = left_side.split('&')
        condition = tuple(term.strip() for term in left_parts)
        if method == "FC":
            knowledge_base[condition] = right_side.strip()
        elif method == "BC":
            knowledge_base.setdefault(right_side.strip(), []).append(condition)
    elif '<=' in expression:
        right_side, left_side = expression.split('<=')
        right_parts = right_side.split('&')
        condition = tuple(term.strip() for term in right_parts)
        if method == "FC":
            knowledge_base[condition] = left_side.strip()
        elif method == "BC":
            knowledge_base.setdefault(left_side.strip(), []).append(condition)
    elif '<->' in expression:
        left_side, right_side = expression.split('<->')
        left_parts = left_side.split('&')
        condition_left = tuple(term.strip() for term in left_parts)
        right_parts = right_side.split('&')
        condition_right = tuple(term.strip() for term in right_parts)
        if method == "FC":
            knowledge_base[condition_left] = right_side.strip()
            knowledge_base[condition_right] = left_side.strip()
        elif method == "BC":
            knowledge_base.setdefault(right_side.strip(), []).append(condition_left)
            knowledge_base.setdefault(left_side.strip(), []).append(condition_right)
    else:
        facts_set.add(expression)
    return knowledge_base, facts_set

def generic_operator_table(expression, knowledge_base, facts_set, level=0):
    for variable, symbol in operator_mapping.items():
        expression = expression.replace(variable, symbol)
    
    if '(' in expression:
        level += 1
        while '(' in expression:
            inner_expressions = re.findall(r'\(([^()]+)\)', expression)
            for inner_expression in inner_expressions:
                generic_operator_table(inner_expression, knowledge_base, facts_set, level)
            expression = re.sub(r'\(([^()]+)\)', '@', expression)
        
        parts = expression.split('=>', 1)
        if '&' in parts[0]:
            left_side = tuple([term.strip() for term in parts[0].split('&')])
            right_side = parts[1].strip()
            knowledge_base.append((left_side, right_side, level))
        elif '||' in parts[0]:
            left_side = tuple(['*' + term.strip() if term.strip() else term.strip() for term in parts[0].split('||')])
            right_side = parts[1].strip()
            knowledge_base.append((left_side, right_side, level)) 
        elif '~' in parts[0]:
            fact = parts[0].strip('~').strip()
            if fact:
                knowledge_base.append((fact, False, level))
        else:
            left_side = tuple(term.strip() for term in parts[0].split('=>'))
            right_side = parts[1].strip()
            knowledge_base.append((left_side, right_side, level))
    elif '<=' in expression:
        parts = expression.split('<=', 1)
        if '&' in parts[1]:
            right_side = tuple([term.strip() for term in parts[1].split('&')])
            left_side = parts[0].strip()
            knowledge_base.append((right_side, left_side, level))
        elif '||' in parts[1]:
            right_side = tuple(['*' + term.strip() if term.strip() else term.strip() for term in parts[1].split('||')])
            left_side = parts[0].strip()
            knowledge_base.append((right_side, left_side, level))
        elif '~' in parts[1]:
            fact = parts[0].strip('~').strip()
            if fact:
                knowledge_base.append((fact, False, level))
        else:
            right_side = tuple(term.strip() for term in parts[1].split('<=')) 
            left_side = parts[0].strip()
            knowledge_base.append((right_side, left_side, level))
    elif '<->' in expression:
        if '&' in expression:
            parts = expression.split('<->', 1)
            left_side = tuple([term.strip() for term in parts[0].split('&')])
            right_side = parts[1].strip()
            knowledge_base.append((left_side, right_side, level))
            knowledge_base.append((tuple(right_side.split('&')), left_side, level))
        elif '||' in expression:
            parts = expression.split('<->', 1)
            left_side = tuple(['*' + term.strip() if term.strip() else term.strip() for term in parts[0].split('||')])
            right_side = parts[1].strip()
            knowledge_base.append((left_side, right_side, level))
            knowledge_base.append((tuple(right_side.split('||')), left_side, level))
        elif '~' in expression:
            fact = expression.strip('~').strip()
            if fact:
                knowledge_base.append((fact, False, level))
        else:
            parts = expression.split('<->', 1)
            left_side = tuple([term.strip() for term in parts[0].split('<->')])
            right_side = parts[1].strip()
            knowledge_base.append((left_side, right_side, level))
            knowledge_base.append((tuple(right_side.split('<->')), left_side, level))
    else:
        facts_set.add(expression)
        facts_set.discard('')
