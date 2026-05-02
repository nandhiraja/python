import re
from dataclasses import dataclass
from typing import Any

@dataclass
class Token:
    type: str
    value: Any

class Lexer:
    # Token types
    FN = "FN"
    LET = "LET"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    RETURN = "RETURN"
    PRINT = "PRINT"
    
    IDENT = "IDENT"
    INT = "INT"
    STRING = "STRING"
    
    ASSIGN = "ASSIGN"
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    
    EQ = "EQ"
    NEQ = "NEQ"
    LT = "LT"
    LTE = "LTE"
    GT = "GT"
    GTE = "GTE"
    
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    COMMA = "COMMA"
    
    EOF = "EOF"

    KEYWORDS = {
        "fn": FN,
        "let": LET,
        "if": IF,
        "else": ELSE,
        "while": WHILE,
        "return": RETURN,
        "print": PRINT
    }

    # Regex patterns for tokens
    TOKEN_REGEX = [
        (r'\s+', None),  # Skip whitespace
        (r'fn\b', FN),
        (r'let\b', LET),
        (r'if\b', IF),
        (r'else\b', ELSE),
        (r'while\b', WHILE),
        (r'return\b', RETURN),
        (r'print\b', PRINT),
        (r'[a-zA-Z_]\w*', IDENT),
        (r'\d+', INT),
        (r'"[^"]*"', STRING),
        (r'==', EQ),
        (r'!=', NEQ),
        (r'<=', LTE),
        (r'>=', GTE),
        (r'<', LT),
        (r'>', GT),
        (r'=', ASSIGN),
        (r'\+', PLUS),
        (r'-', MINUS),
        (r'\*', STAR),
        (r'/', SLASH),
        (r'\(', LPAREN),
        (r'\)', RPAREN),
        (r'\{', LBRACE),
        (r'\}', RBRACE),
        (r',', COMMA),
    ]

    def __init__(self, source: str):
        self.source = source
        self.pos = 0

    def tokenize(self) -> list[Token]:
        tokens = []
        while self.pos < len(self.source):
            match = None
            for pattern, token_type in self.TOKEN_REGEX:
                regex = re.compile(pattern)
                match = regex.match(self.source, self.pos)
                if match:
                    if token_type:
                        value = match.group(0)
                        if token_type == self.INT:
                            value = int(value)
                        elif token_type == self.STRING:
                            value = value[1:-1] # strip quotes
                        tokens.append(Token(token_type, value))
                    self.pos = match.end(0)
                    break
            
            if not match:
                raise SyntaxError(f"Unexpected character at position {self.pos}: {self.source[self.pos]}")

        tokens.append(Token(self.EOF, None))
        return tokens
