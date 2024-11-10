import sys
from typing import Set
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
import argparse

from truth_table import parse_truth_table_file, evaluate_truth_table, evaluate_generic_truth_table
from forward_chaining import parse_chain_file, forward_chaining
from backward_chaining import backward_chaining

class InferenceMethod(Enum):
    TRUTH_TABLE = "TT"
    FORWARD_CHAINING = "FC"
    BACKWARD_CHAINING = "BC"

@dataclass
class InferenceResult:
    is_valid: bool
    derived_facts: Set[str] = None
    error_message: str = None

class InferenceEngine:    
    def process_truth_table(self, filename):
        try:
            knowledge_base, fact_set, query, bracket_flag = parse_truth_table_file(filename)
            if bracket_flag == 0:
                result = evaluate_truth_table(knowledge_base, fact_set, query)
            else:
                result = evaluate_generic_truth_table(knowledge_base, fact_set, query)
            return InferenceResult(is_valid=result)
            
        except Exception as e:
            return InferenceResult(is_valid=False, error_message=str(e))

    def process_forward_chaining(self, filename):
        try:
            knowledge_base, fact_set, query = parse_chain_file(filename, "FC")
            result = forward_chaining(knowledge_base, fact_set, query)
            return InferenceResult(is_valid=result)
            
        except Exception as e:
            return InferenceResult(is_valid=False, error_message=str(e))

    def process_backward_chaining(self, filename):
        try:
            knowledge_base, fact_set, query = parse_chain_file(filename, "BC")
            derived_facts = set()
            result = backward_chaining(knowledge_base, fact_set, query, derived_facts)
            return InferenceResult(is_valid=result, derived_facts=derived_facts)
            
        except Exception as e:
            return InferenceResult(is_valid=False, error_message=str(e))

def parse_arguments():
    parser = argparse.ArgumentParser(description='Inference Engine')
    parser.add_argument('filename', type=Path, help='Path to the input file')
    parser.add_argument('method', type=str, choices=[m.value for m in InferenceMethod], 
                        help='Inference method to use')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    if not args.filename.exists():
        print(f"Error: File {args.filename} does not exist")
        sys.exit(1)
        
    engine = InferenceEngine()
    
    try:
        if args.method == InferenceMethod.TRUTH_TABLE.value:
            result = engine.process_truth_table(args.filename)
        elif args.method == InferenceMethod.FORWARD_CHAINING.value:
            result = engine.process_forward_chaining(args.filename)
        elif args.method == InferenceMethod.BACKWARD_CHAINING.value:
            result = engine.process_backward_chaining(args.filename)
        
        if result.error_message:
            print(f"Error: {result.error_message}")
            sys.exit(1)
        else:
            print(result.is_valid)
            if result.derived_facts:
                print(f"Derived facts: {result.derived_facts}")
                
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()