from dataclasses import dataclass
from typing import Any, List, Optional

class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]
    
    def __repr__(self):
        return f"Program(statements={self.statements})"

@dataclass
class FunctionDecl(ASTNode):
    name: str
    params: List[str]
    body: List[ASTNode]

    def __repr__(self):
        return f"FunctionDecl(name={self.name}, params={self.params})"

@dataclass
class LetDecl(ASTNode):
    name: str
    value: ASTNode

    def __repr__(self):
        return f"LetDecl(name={self.name}, value={self.value})"

@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_branch: List[ASTNode]
    else_branch: Optional[List[ASTNode]]

    def __repr__(self):
        return f"IfStatement(condition={self.condition})"

@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: List[ASTNode]

@dataclass
class ReturnStmt(ASTNode):
    value: Optional[ASTNode]

    def __repr__(self):
        return f"ReturnStmt(value={self.value})"

@dataclass
class PrintStmt(ASTNode):
    value: ASTNode

    def __repr__(self):
        return f"PrintStmt(value={self.value})"

@dataclass
class ExprStmt(ASTNode):
    expr: ASTNode

@dataclass
class BinOp(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode

    def __repr__(self):
        return f"BinOp(op={self.op}, left={self.left}, right={self.right})"

@dataclass
class Call(ASTNode):
    name: str
    args: List[ASTNode]

    def __repr__(self):
        return f"Call(name={self.name}, args={self.args})"

@dataclass
class Ident(ASTNode):
    name: str

    def __repr__(self):
        return f"Ident(name={self.name})"

@dataclass
class Literal(ASTNode):
    value: Any

    def __repr__(self):
        if isinstance(self.value, str):
            return f'Literal("{self.value}")'
        return f"Literal({self.value})"

@dataclass
class StringLiteral(ASTNode):
    value: str
    
    def __repr__(self):
        return f'StringLiteral("{self.value}")'
