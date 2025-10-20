class ProgramContext:
    """Models the context of a program."""
    def __init__(self, indeterminates: set[str]):
        """Creates a new ProgramContext object,

        Args:
            indeterminates (set[str]): The set of indeterminates of the program (including the constant one).
        """
        self.indeterminates = indeterminates
