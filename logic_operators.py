import re
from itertools import product

universal_variables = {
    '^': '&', '∧': '&',
    '|': '||',
    '¬': '~', '!': '~',
    '->': '=>', '→': '=>',
    '<-': '<=', '←': '<=',
    '<=>': '<->', '↔': '<->',
}

def operator_table(part, kb, facts):
    for variable, symbol in universal_variables.items():
        part = part.replace(variable, symbol)
    if '=>' in part:
        parts = part.split('=>')
        if '&' in parts[0]:
            left = tuple([c.strip() for c in parts[0].split('&')])
            right = parts[1].strip()
            kb.append((left, right))
        elif '||' in parts[0]:
            left = tuple(['*' + c.strip() if c.strip() else c.strip() for c in parts[0].split('||')])
            right = parts[1].strip()
            kb.append((left, right))
        elif '~' in parts[0]:
            fact = parts[0].strip('~').strip()
            if fact:
                kb.append(fact, False)
        else:
            left = tuple(c.strip() for c in parts[0].split('=>'))
            right = parts[1].strip()
            kb.append((left, right))
    elif '<=' in part:
        parts = part.split('<=')
        if '&' in parts[1]:
            right = tuple([c.strip() for c in parts[1].split('&')])
            left = parts[0].strip()
            kb.append((right, left))
        elif '||' in parts[1]:
            right = tuple(['*' + c.strip() if c.strip() else c.strip() for c in parts[1].split('||')])
            left = parts[0].strip()
            kb.append((right, left))
        elif '~' in parts[1]:
            fact = parts[0].strip('~').strip()
            if fact:
                kb.append(fact, False)
        else:
            right = tuple(c.strip() for c in parts[1].split('<=')) 
            left = parts[0].strip()
            kb.append((right, left))
    elif '<->' in part:
        if '&' in part:
            parts = part.split('<->')
            left = tuple([c.strip() for c in parts[0].split('&')])
            right = parts[1].strip()
            kb.append((left, right))
            kb.append((tuple(right.split('&')), left))
        elif '||' in part:
            parts = part.split('<->')
            left = tuple(['*' + c.strip() if c.strip() else c.strip() for c in parts[0].split('||')])
            right = parts[1].strip()
            kb.append((left, right))
            kb.append((tuple(right.split('||')), left))
        elif '~' in part:
            fact = part.strip('~').strip()
            if fact:
                kb.append(fact, False)
        else:
            parts = part.split('<->')
            left = tuple([c.strip() for c in parts[0].split('<->')])
            right = parts[1].strip()
            kb.append((left, right))
            kb.append((tuple(right.split('<->')), left))
    else:
        facts.add(part)
        facts.discard('')
    return part, facts 

def operator_chain(part, method, kb, facts):
    for variable, symbol in universal_variables.items():
        part = part.replace(variable, symbol)
    if '(' in part or '||' in part or '~' in part:
        print("Generic KB is not applicable to FC and BC method.")
        return
    if '=>' in part:
        left, right = part.split('=>')
        left_parts = left.split('&')
        condition = tuple(c.strip() for c in left_parts)
        if method == "FC":
            kb[condition] = right.strip()
        elif method == "BC":
            kb.setdefault(right.strip(), []).append(condition)
    elif '<=' in part:
        right, left = part.split('<=')
        right_parts = right.split('&')
        condition = tuple(c.strip() for c in right_parts)
        if method == "FC":
            kb[condition] = left.strip()
        elif method == "BC":
            kb.setdefault(left.strip(), []).append(condition)
    elif '<->' in part:
        left, right = part.split('<->')
        left_parts = left.split('&')
        condition_left = tuple(c.strip() for c in left_parts)
        right_parts = right.split('&')
        condition_right = tuple(c.strip() for c in right_parts)
        if method == "FC":
            kb[condition_left] = right.strip()
            kb[condition_right] = left.strip()
        elif method == "BC":
            kb.setdefault(right.strip(), []).append(condition_left)
            kb.setdefault(left.strip(), []).append(condition_right)
    else:
        facts.add(part)
    return kb, facts

def generic_operator_table(part, kb, facts, level=0):
    for variable, symbol in universal_variables.items():
        part = part.replace(variable, symbol)
    if '(' in part:
        level += 1
        while '(' in part:
            inner_parts = re.findall(r'\(([^()]+)\)', part)
            for inner_part in inner_parts:
                generic_operator_table(inner_part, kb, facts, level)
            part = re.sub(r'\(([^()]+)\)', '@', part)
        parts = part.split('=>', 1)
        if '&' in parts[0]:
            left = tuple([c.strip() for c in parts[0].split('&')])
            right = parts[1].strip()
            kb.append((left, right, level))
        elif '||' in parts[0]:
            left = tuple(['*' + c.strip() if c.strip() else c.strip() for c in parts[0].split('||')])
            right = parts[1].strip()
            kb.append((left, right, level)) 
        elif '~' in parts[0]:
            fact = parts[0].strip('~').strip()
            if fact:
                kb.append(fact, False, level)
        else:
            left = tuple(c.strip() for c in parts[0].split('=>'))
            right = parts[1].strip()
            kb.append((left, right, level))
    elif '<=' in part:
        parts = part.split('<=', 1)
        if '&' in parts[1]:
            right = tuple([c.strip() for c in parts[1].split('&')])
            left = parts[0].strip()
            kb.append((right, left), level)
        elif '||' in parts[1]:
            right = tuple(['*' + c.strip() if c.strip() else c.strip() for c in parts[1].split('||')])
            left = parts[0].strip()
            kb.append((right, left), level)
        elif '~' in parts[1]:
            fact = parts[0].strip('~').strip()
            if fact:
                kb.append(fact, False, level)
        else:
            right = tuple(c.strip() for c in parts[1].split('<=')) 
            left = parts[0].strip()
            kb.append((right, left, level))
    elif '<->' in part:
        if '&' in part:
            parts = part.split('<->', 1)
            left = tuple([c.strip() for c in parts[0].split('&')])
            right = parts[1].strip()
            kb.append((left, right, level))
            kb.append((tuple(right.split('&')), left, level))
        elif '||' in part:
            parts = part.split('<->', 1)
            left = tuple(['*' + c.strip() if c.strip() else c.strip() for c in parts[0].split('||')])
            right = parts[1].strip()
            kb.append((left, right, level))
            kb.append((tuple(right.split('||')), left, level))
        elif '~' in part:
            fact = part.strip('~').strip()
            if fact:
                kb.append(fact, False, level)
        else:
            parts = part.split('<->', 1)
            left = tuple([c.strip() for c in parts[0].split('<->')])
            right = parts[1].strip()
            kb.append((left, right, level))
            kb.append((tuple(right.split('<->')), left, level))
    else:
        facts.add(part)
        facts.discard('')     
    return kb, facts
