import sys
from typing import Set
from pathlib import Path
from enum import Enum 
from dataclasses import dataclass 
import argparse 

#importing necessary modules for the different inference methods and truth table, dpll operations
from truth_table import parse_truth_table_file, evaluate_truth_table, evaluate_generic_truth_table
from forward_chaining import parse_chain_file, forward_chaining
from backward_chaining import backward_chaining
from dpll import process_dpll_file

#defines different types of inference methods supported
class InferenceMethod(Enum): 
    TRUTH_TABLE = "TT"
    FORWARD_CHAINING = "FC"
    BACKWARD_CHAINING = "BC"
    DPLL = "DPLL"

#dataclass to represent the result of an inference operation
@dataclass
class InferenceResult: 
    is_valid: bool #used for indicating whether or not inference was successful
    derived_facts: Set[str] = None #set of facts derived during inference
    error_message: str = None #error msg in case of failure

#main engine to process the different inference methods
class InferenceEngine:    
    def process_truth_table(self, filename): #processes file using the truth table method
        try: 
            knowledge_base, fact_set, query, bracket_flag = parse_truth_table_file(filename) #parse file
            if bracket_flag == 0: #evauluate based on bracket flag
                result = evaluate_truth_table(knowledge_base, fact_set, query)
            else:
                result = evaluate_generic_truth_table(knowledge_base, fact_set, query)
            return InferenceResult(is_valid=result) #return a successful inference result
             
        except Exception as e: #handle exceptions and return error result
            return InferenceResult(is_valid=False, error_message=str(e))

    def process_forward_chaining(self, filename): #processes a file using the forward chaining method
        try:
            knowledge_base, fact_set, query = parse_chain_file(filename, "FC")
            result = forward_chaining(knowledge_base, fact_set, query)
            return InferenceResult(is_valid=result)
            
        except Exception as e:
            return InferenceResult(is_valid=False, error_message=str(e))

    def process_backward_chaining(self, filename): #processes file using backward chaining method
        try:
            knowledge_base, fact_set, query = parse_chain_file(filename, "BC")
            derived_facts = set()
            result = backward_chaining(knowledge_base, fact_set, query, derived_facts)
            return InferenceResult(is_valid=result, derived_facts=derived_facts)
            
        except Exception as e:
            return InferenceResult(is_valid=False, error_message=str(e))
    
    def process_dpll(self, filename): #processes file using DPLL algorthim method
        try:
            result = process_dpll_file(filename)
            return InferenceResult(is_valid=result)
        except Exception as e:
            return InferenceResult(is_valid=False, error_message=str(e))

#parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Inference Engine')
    parser.add_argument('filename', type=Path, help='Path to the input file')
    parser.add_argument('method', type=str, choices=[m.value for m in InferenceMethod], 
                        help='Inference method to use')
    return parser.parse_args()

#main function to run the inference engine
def main():
    args = parse_arguments()
    
    #check if the provided file exisits
    if not args.filename.exists():
        print(f"Error: File {args.filename} does not exist")
        sys.exit(1)
        
    #initialize the inference engine
    engine = InferenceEngine()
    
    try:
        #execute the appropriate inference method based on the user's choice
        if args.method == InferenceMethod.TRUTH_TABLE.value:
            result = engine.process_truth_table(args.filename)
        elif args.method == InferenceMethod.FORWARD_CHAINING.value:
            result = engine.process_forward_chaining(args.filename)
        elif args.method == InferenceMethod.BACKWARD_CHAINING.value:
            result = engine.process_backward_chaining(args.filename)
        elif args.method == InferenceMethod.DPLL.value:
            result = engine.process_dpll(args.filename)
        
        #handle the results and print output
        if result.error_message:
            print(f"Error: {result.error_message}")
            sys.exit(1)
        else:
            print(result.is_valid)
            if result.derived_facts:
                print(f"Derived facts: {result.derived_facts}")
                
    except Exception as e:
        #handle the unexpected errors
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()