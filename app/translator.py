"""Conservative Boolean IEC Structured Text subset translator. Not safety-verified."""
import re
from dataclasses import dataclass

class TranslationError(ValueError):
    pass

TOK = re.compile(r"\s*(?:(AND|OR|NOT|TRUE|FALSE)\b|([A-Za-z_][A-Za-z_0-9]*)|([():;=]))", re.I)
@dataclass
class Node:
    op: str
    args: tuple = ()

def tokenize(s):
    out = []
    p = 0
    while p < len(s):
        if s[p:].strip() == "":
            break
        m = TOK.match(s, p)
        if not m:
            raise TranslationError(f"Unsupported syntax at character {p}: {s[p:p+25]!r}")
        out.append((m.group(1) or m.group(2) or m.group(3)).upper() if m.group(1) else (m.group(2) or m.group(3)))
        p = m.end()
    return out

class Parser:
    def __init__(self, t):
        self.t, self.i = t, 0
    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None
    def eat(self, expected=None):
        x = self.peek()
        if x is None or (expected is not None and x != expected):
            raise TranslationError(f"Expected {expected or 'token'}; got {x!r}")
        self.i += 1
        return x
    def atom(self):
        if self.peek() == "NOT":
            self.eat()
            return Node("NOT", (self.atom(),))
        if self.peek() == "(":
            self.eat()
            n = self.expr()
            self.eat(")")
            return n
        x = self.eat()
        if x in ("TRUE", "FALSE"):
            return Node(x)
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", x) or x.upper() in ("AND", "OR", "NOT"):
            raise TranslationError("Expected variable or Boolean literal")
        return Node("VAR", (x,))
    def and_expr(self):
        n = self.atom()
        while self.peek() == "AND":
            self.eat()
            n = Node("AND", (n, self.atom()))
        return n
    def expr(self):
        n = self.and_expr()
        while self.peek() == "OR":
            self.eat()
            n = Node("OR", (n, self.and_expr()))
        return n

def parse(source):
    if len(source) > 20000:
        raise TranslationError("Input exceeds 20,000 characters")
    if "(*" in source or "//" in source:
        raise TranslationError("Comments not supported in this subset")
    t = tokenize(source)
    p = Parser(t)
    dest = p.eat()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", dest) or dest.upper() in ("AND", "OR", "NOT", "TRUE", "FALSE"):
        raise TranslationError("Invalid assignment target")
    p.eat(":")
    p.eat("=")
    node = p.expr()
    p.eat(";")
    if p.peek() is not None:
        raise TranslationError("Only one Boolean assignment is supported")
    return dest, node

def render_st(n):
    if n.op == "VAR":
        return n.args[0]
    if n.op in ("TRUE", "FALSE"):
        return n.op
    if n.op == "NOT":
        return f"NOT ({render_st(n.args[0])})"
    return f"({render_st(n.args[0])} {n.op} {render_st(n.args[1])})"

def render_ld(n):
    if n.op == "VAR":
        return f"[ {n.args[0]} ]"
    if n.op == "NOT" and n.args[0].op == "VAR":
        return f"[/ {n.args[0].args[0]} ]"
    if n.op == "AND":
        return f"{render_ld(n.args[0])} -- {render_ld(n.args[1])}"
    if n.op == "OR":
        return f"PARALLEL( {render_ld(n.args[0])} | {render_ld(n.args[1])} )"
    raise TranslationError("This expression cannot be represented by the supported ladder notation")

def translate(source, target_language, target_platform):
    if target_language not in ("st", "ld"):
        raise TranslationError("Only ST and illustrative LD notation are supported")
    if target_platform not in ("generic", "codesys", "siemens", "rockwell", "beckhoff"):
        raise TranslationError("Unsupported platform")
    dest, node = parse(source)
    if target_language == "st":
        output = f"{dest} := {render_st(node)};"
        status = "subset_translation_not_compiled"
    else:
        output = f"|-- {render_ld(node)} --( {dest} )--|"
        status = "illustrative_ladder_not_importable"
    return {"output": output, "status": status, "source_language": "st", "target_language": target_language,
            "target_platform": target_platform, "warnings": [
                "Not compiled against a vendor toolchain.",
                "No behavioral equivalence or functional safety verification performed.",
                "Vendor-specific semantics, task scheduling, I/O mapping, and controller compatibility are not verified."
            ], "scope": "Single Boolean assignment with AND, OR, NOT and parentheses; no declarations, timers, counters or function blocks."}
