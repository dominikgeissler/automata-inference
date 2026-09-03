def get_grammar():
    """Returns the grammar for the parser."""
    return r"""
%ignore /#.*$/m
%ignore /\/\/.*$/m
%ignore WS
%ignore ";"

%import common.CNAME
%import common.INT
%import common.WS

program: declarations statements query?

declarations:    declaration*   -> declarations
statements:      statement*     -> statements

declaration:    "var" var       -> var

statement:      "skip"                              -> skip
        |       var ":=" rhs                        -> assignment
        |       var "+=" rhs                        -> increment
        |       var "--"                            -> monus
        |       block "[" frac "]" block            -> probchoice
        |       "if" par_block block ("else" block)?  -> if
        |       "observe" par_block                 -> observe
        |       "while" par_block block             -> while

query:      "?Pr[" guard "]"            -> posterior_prob
        |   "?E[" var "," INT "]"       -> moment
        |   "?E[" var "," var "]"       -> mixed_moment

block: "{" statement* "}"
par_block: "(" guard ")"

guard:  var "<" INT             -> lt
    |   var "%" INT "="? INT    -> mod
    |   var "=" INT             -> eq
    |   var "<=" INT            -> leq
    |   var ">=" INT            -> geq
    |   var ">" INT             -> gt
    |   var "!=" INT            -> neq
    |   guard "->" guard        -> impl
    |   guard "&&" guard        -> land
    |   guard "||" guard        -> lor
    |   "!" par_block           -> neg

rhs:    INT                                     -> const
    |   "iid" "(" distribution "," var  ")"     -> iid
    |   distribution                            -> distribution
    |   var                                     -> var

distribution:   "Unif" "(" INT ")"                  -> uniform
        |       "Geom" "(" frac")"                  -> geometric
        |       "NegBinom" "(" INT "," frac ")"     -> negbinom
        |       "Bern" "(" frac ")"                 -> bernoulli
        |       "Dirac" "(" INT ")"                 -> dirac

frac:   INT "/" INT     -> frac

var: CNAME
    """