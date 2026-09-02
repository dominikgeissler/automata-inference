import time

from argparse import ArgumentParser
import sys
from automata_inference.automata_factory import PGAFactory
from automata_inference.parser.parser import parse
from automata_inference.visualizer import visualize



def main(program_path, visualize_posterior):
    program = parse(program_path)
    
    print()
    print("----------------------------------")
    print("-       Starting Analysis        -")
    print("----------------------------------")
    print()
    
    input_pga = PGAFactory.one((program.variables | {"1"}))
    start = time.time()
    out = program.apply_semantics(input_pga)
    print()
    print("----------------------------------")
    print("-       Finished Analysis        -")
    print(f"- in {round(time.time() - start, 17)} seconds -")
    print("----------------------------------")
    print()

    if program.query:
        print(f"Output of '{program.query}': {program.evaluate_query(out)}")
    if visualize_posterior:
        visualize(out, view=True)
    
    

def create_parser():
    parser = ArgumentParser(
        description="Anaylsis of discrete probabilistic programs."
    )

    parser.add_argument(
        "program_path",
        help="Path to the program file."
    )
    
    parser.add_argument(
        "--visualize-posterior",
        action="store_true",
        help="If set, renders the automaton representation of the normalized posterior distribution."
    )

    return parser

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    main(program_path=args.program_path, visualize_posterior=args.visualize_posterior)