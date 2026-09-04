from automata_inference.automata.factory import DFAFactory, PGAFactory
from automata_inference.automata.model import (
    PGA,
    State,
    Transition,
    new_state_namespace,
)
from automata_inference.parser.ast.statements import (
    AssignStatement,
    CoinflipStatement,
    ConstantRhs,
    DistributionRhs,
    IfStatement,
    IidRhs,
    IncrementStatement,
    MonusStatement,
    ObserveStatement,
    Program,
    Rhs,
    SequentialCompositionStatement,
    SkipStatement,
    Statement,
    VariableRhs,
)
from automata_inference.programs.handlers.distribution_handler import (
    DistributionHandler,
)
from automata_inference.programs.handlers.guard_handler import GuardHandler
from automata_inference.programs.handlers.query_handler import QueryHandler

compile_distribution = DistributionHandler.compile
evaluate_query = QueryHandler.evaluate_query


class StatementHandler:
    """Handles the compilation of parsed statements into automaton transformations."""
    def __init__(self, indeterminates: set[str]):
        """Creates a new StatementHandler instance.

        Args:
            indeterminates (set[str]): The set of indeterminates within the program.
        """
        self.indeterminates = indeterminates
        self.guard_handler = GuardHandler(indeterminates)

    def compile_program(self, program: Program, pga: PGA) -> PGA:
        """Applies the semantics of a given program to an input PGA. Also computes the result of any query present in the program.

        Args:
            program (Program): The parsed program to be compiled.
            pga (PGA): The input PGA to which the program semantics will be applied.

        Returns:
            PGA: The resulting PGA after applying the program semantics (and normalization, if an observe-statement has been used).
        """
        res = pga
        if program.body:
            res = self._compile(program.body, pga)
        if program.is_observe:
            res = res.normalize()
        if program.query:
            print("Evaluating query ....")
            query_result = evaluate_query(program.query, res)
            print(f"Result: {query_result}")
        return res

    def _compile(self, statement: Statement, pga: PGA) -> PGA:
        """Compile one statement into an automaton transformation."""
        if isinstance(statement, SkipStatement):
            return pga
        if isinstance(statement, AssignStatement):
            return self._compile_assignment(statement, pga)
        if isinstance(statement, IncrementStatement):
            return self._compile_increment(statement, pga)
        if isinstance(statement, MonusStatement):
            return self._compile_monus(statement, pga)
        if isinstance(statement, CoinflipStatement):
            return self._compile_coinflip(statement, pga)
        if isinstance(statement, IfStatement):
            return self._compile_if(statement, pga)
        if isinstance(statement, ObserveStatement):
            return self._compile_observe(statement, pga)
        if isinstance(statement, SequentialCompositionStatement):
            return self._compile_sequence(statement, pga)
        raise ValueError(f"Unsupported statement type: {type(statement)}")
    
    def _compile_assignment(self, statement: AssignStatement, pga: PGA) -> PGA:
        indeterminate = statement.variable
        return self._compile_rhs(
            statement.rhs, indeterminate, pga.substitute(indeterminate, 1)
        )

    def _compile_increment(self, statement: IncrementStatement, pga: PGA) -> PGA:
        return self._compile_rhs(statement.rhs, statement.variable, pga)

    def _compile_monus(self, statement: MonusStatement, pga: PGA) -> PGA:
        return pga.decrement(statement.variable)

    def _compile_coinflip(self, statement: CoinflipStatement, pga: PGA) -> PGA:
        res_left: PGA = self._compile(statement.left, pga)
        res_right: PGA = self._compile(statement.right, pga)
        return res_left.weighted_union(res_right, statement.p, 1 - statement.p)

    def _compile_if(self, statement: IfStatement, pga: PGA) -> PGA:
        guard_dfa = self.guard_handler.compile(statement.guard)
        neg_guard_dfa = DFAFactory.neg(guard_dfa)
        filtered_then = pga.filter(guard_dfa)
        filtered_else = pga.filter(neg_guard_dfa)
        res_left = self._compile(statement.then_statement, filtered_then)
        if statement.else_statement is None:
            return res_left
        res_right = self._compile(statement.else_statement, filtered_else)
        return res_left.weighted_union(res_right, 1, 1)

    def _compile_observe(self, statement: ObserveStatement, pga: PGA) -> PGA:
        return pga.filter(self.guard_handler.compile(statement.guard))

    def _compile_sequence(
        self, statement: SequentialCompositionStatement, pga: PGA
    ) -> PGA:
        return self._compile(statement.right, self._compile(statement.left, pga))

    def _compile_rhs(self, rhs: Rhs, indeterminate: str, pga: PGA) -> PGA:
        if isinstance(rhs, ConstantRhs):
            return pga.concat(PGAFactory.dirac(indeterminate, rhs.value))
        if isinstance(rhs, VariableRhs):
            namespace = new_state_namespace()
            s0, s1, s2 = State(namespace, 0), State(namespace, 1), State(namespace, 2)
            subs = PGA(
                {s0, s1, s2},
                {
                    Transition(s0, s1, symbol=rhs.variable),
                    Transition(s1, s2, symbol=indeterminate),
                },
                {(1, s0)},
                {(1, s2)},
            )
            return pga.transition_substitution(rhs.variable, subs)
        if isinstance(rhs, DistributionRhs):
            return pga.concat(compile_distribution(rhs.distribution, indeterminate))
        if isinstance(rhs, IidRhs):
            other_dirac = PGAFactory.dirac(rhs.variable, 1)
            distribution_iid = compile_distribution(rhs.distribution, indeterminate)
            subs = other_dirac.concat(distribution_iid)
            return pga.transition_substitution(rhs.variable, subs)
        raise ValueError(f"Unsupported RHS type: {type(rhs)}")
