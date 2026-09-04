import time

from argparse import ArgumentParser
import sys
from automata_inference.automata.factory import PGAFactory
from automata_inference.parser.parser import parse


def main(program_path: str, visualize_posterior: bool):
    """Main method of the program.

    Args:
        program_path (str): The path to the program file to be analyzed.
        visualize_posterior (bool): Indicates whether the normalized posterior should be visually depicted.
    """
    program = parse(program_path)
    print(program)
    return

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
    """Creates and returns the parser of the CLI arguments."""
    argument_parser = ArgumentParser(description="Anaylsis of discrete probabilistic programs.")

    argument_parser.add_argument("program_path", help="Path to the program file.")

    argument_parser.add_argument(
        "--visualize-posterior",
        action="store_true",
        help="If set, renders the automaton representation of the normalized posterior distribution.",
    )

    return argument_parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    main(program_path=args.program_path, visualize_posterior=args.visualize_posterior)
