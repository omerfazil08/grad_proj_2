# simplifier_phase74.py
# Robust simplifier that converts arbitrary gate networks to pure AND/OR/NOT
# expressions (no SymPy Xor nodes). Uses to_dnf on the cleaned expression.
#
# Improvements over original:
# - NO "n" prefix guessing (previously mis-parsed many tokens as NOT)
# - XOR / XNOR expanded into AND/OR/NOT identities before DNF
# - Handles NAND/NOR/MUX2 by expansion
# - Defensive fallback if to_dnf fails

from sympy import symbols, And, Or, Not
from sympy.logic.boolalg import to_dnf
from typing import List, Dict

print("✅ Loaded simplifier_phase74 (robust XOR-aware DNF)")

# --- Symbol cache to reuse sympy symbols ---
_sym_cache = {}

def sym(name: str):
    """Return a sympy Symbol for the given name, reusing cached objects."""
    if name not in _sym_cache:
        _sym_cache[name] = symbols(name)
    return _sym_cache[name]

# --- Helper builders for gate semantics ---
# We intentionally avoid constructing SymPy Xor nodes; instead we expand XOR/XNOR
# into AND/OR/NOT so the result is compatible with to_dnf and avoids weird types.

def expand_xor(a, b):
    # a XOR b = (a & ~b) | (~a & b)
    return Or(And(a, Not(b)), And(Not(a), b))

def expand_xnor(a, b):
    # a XNOR b = NOT(a XOR b) = (a & b) | (~a & ~b)
    return Or(And(a, b), And(Not(a), Not(b)))

def expand_nand(args):
    # NAND(args) = NOT(AND(args))
    return Not(And(*args))

def expand_nor(args):
    # NOR(args) = NOT(OR(args))
    return Not(Or(*args))

def expand_mux2(s, a, b):
    # MUX2(s, a, b) = (~s & a) | (s & b)
    return Or(And(Not(s), a), And(s, b))

def expand_full_sum(a, b, c):
    # full adder sum = a XOR b XOR c
    # expand iteratively with expand_xor to ensure only And/Or/Not produced
    return expand_xor(expand_xor(a, b), c)

def expand_full_carry(a, b, c):
    # full carry = (a & b) | (a & c) | (b & c)
    return Or(And(a, b), And(a, c), And(b, c))

# Map gate-name -> factory that accepts list of arg expressions
GATE_FACTORY = {
    "AND": lambda args: And(*args),
    "OR": lambda args: Or(*args),
    "NOT": lambda args: Not(args[0]),
    "XOR": lambda args: expand_xor(args[0], args[1]),
    "XOR2": lambda args: expand_xor(args[0], args[1]),
    "XNOR": lambda args: expand_xnor(args[0], args[1]),
    "XNOR2": lambda args: expand_xnor(args[0], args[1]),
    "NAND": lambda args: expand_nand(args),
    "NOR": lambda args: expand_nor(args),
    "MUX2": lambda args: expand_mux2(args[0], args[1], args[2]),
    "HALF_SUM": lambda args: expand_xor(args[0], args[1]),
    "HALF_CARRY": lambda args: And(args[0], args[1]),
    "FULL_SUM": lambda args: expand_full_sum(args[0], args[1], args[2]),
    "FULL_CARRY": lambda args: expand_full_carry(args[0], args[1], args[2]),
    # Fallbacks: treat unknown gate types as AND of inputs
}

# --- Build expression map from network ---
def build_sym_expr_map(network: List[Dict[str, object]]) -> Dict[str, object]:
    """
    Build a map from gate/output name -> sympy boolean expression.
    `network` is list of dicts: {'name': 'G0', 'type': 'AND', 'inputs': ['A0','G1', ...], 'output': 'G0'}
    We assume inputs are strings like 'A0' or 'G5'. convert_for_simplifier should have created
    these names. We do NOT make any 'n' prefix assumptions here.
    """
    expr = {}
    # NOTE: iterate in order; gates should reference previously defined names where appropriate,
    # but we also allow forward refs by building a dependency-first resolution loop below.
    # Simpler approach: attempt to resolve iteratively until no changes.
    unresolved = list(network)  # shallow copy

    # Iteratively resolve gates; if a gate's inputs are all either input symbols or already-resolved
    # gates, then build its expression.
    input_symbols = set()  # collect input tokens seen (A0, A1, ...)
    for gate in network:
        for tok in gate.get("inputs", []):
            if isinstance(tok, str) and tok.startswith("A"):
                input_symbols.add(tok)

    # Prepopulate input symbols with sympy symbols
    for in_name in input_symbols:
        expr[in_name] = sym(in_name)

    # repeat until resolved or stuck
    progress = True
    while unresolved and progress:
        progress = False
        remaining = []
        for gate in unresolved:
            out_name = gate.get("output", gate.get("name"))
            gtype = gate.get("type")
            raw_inputs = gate.get("inputs", [])
            # Are all inputs resolvable?
            args = []
            resolvable = True
            for tok in raw_inputs:
                if tok in expr:
                    args.append(expr[tok])
                else:
                    # If input is of pattern A\d+ treat as sym; else if it starts with G but not resolved, not resolvable yet.
                    if isinstance(tok, str) and tok.startswith("A"):
                        # create symbol on the fly
                        expr[tok] = sym(tok)
                        args.append(expr[tok])
                    else:
                        resolvable = False
                        break
            if not resolvable:
                remaining.append(gate)
                continue

            # Build expression for gate type
            factory = GATE_FACTORY.get(gtype, None)
            try:
                if factory:
                    built = factory(args)
                else:
                    # unknown gate type -> conservative: AND of arguments
                    built = And(*args) if args else sym("False")
                expr[out_name] = built
                progress = True
            except Exception as e:
                # If a gate fails to build, create a safe placeholder symbol to avoid crashing.
                # This prevents one bad gate from killing the whole simplification.
                expr[out_name] = sym(out_name)
                progress = True

        unresolved = remaining

    # For any leftover unresolved gates (due to cycles or forward refs), make placeholder symbols.
    for gate in unresolved:
        out_name = gate.get("output", gate.get("name"))
        if out_name not in expr:
            expr[out_name] = sym(out_name)

    return expr

# --- Main simplification API ---
def simplify_genome(best_individual: List[Dict], input_names: List[str], output_gate_names: List[str]) -> Dict[str, str]:
    """
    Convert `best_individual` (list of gates in convert_for_simplifier format) into a dict:
    { "Output i (Gx)": "<DNF string>" }
    - best_individual: [{'name':'G0','type':'AND','inputs':['A0','G1'], 'output':'G0'}, ...]
    - input_names: list like ['A0','A1',...]
    - output_gate_names: list like ['G0','G5', ...] (targets)
    """
    expr_map = build_sym_expr_map(best_individual)
    results = {}

    for i, out_gate in enumerate(output_gate_names):
        key = f"Output {i+1} ({out_gate})"
        if out_gate not in expr_map:
            # produce empty / zero in case missing
            results[key] = "False"
            continue
        raw_expr = expr_map[out_gate]

        # Try to produce a DNF string. Catch failures.
        try:
            # to_dnf expects expressions built from And/Or/Not.
            # Our builders expand XOR/XNOR/NAND/NOR/MUX to those primitives.
            final_expr = to_dnf(raw_expr, simplify=True)
            # Convert to string. Str is acceptable for downstream parse_expr usage.
            results[key] = str(final_expr)
        except Exception as e:
            # Fallback: if to_dnf fails or explodes, return a safe stringified version of the raw expr.
            # This at least gives something usable to the caller.
            try:
                results[key] = str(raw_expr)
            except Exception:
                results[key] = "False"

    return results
