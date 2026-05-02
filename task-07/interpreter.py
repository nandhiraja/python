import ast_nodes as ast
from typing import Any, Dict, Optional

class ReturnException(Exception):
    def __init__(self, value: Any):
        self.value = value

class Environment:
    def __init__(self, parent: Optional['Environment'] = None):
        self.variables: Dict[str, Any] = {}
        self.parent = parent

    def define(self, name: str, value: Any):
        self.variables[name] = value

    def assign(self, name: str, value: Any):
        if name in self.variables:
            self.variables[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise NameError(f"Undefined variable '{name}'.")

    def get(self, name: str) -> Any:
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Undefined variable '{name}'.")

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.env = self.global_env
        self.output = []
        
        # Add builtins
        self.global_env.define("str", lambda arg: str(arg))

    def evaluate(self, node: ast.ASTNode) -> Any:
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ast.ASTNode):
        raise Exception(f"No visit_{type(node).__name__} method")

    def execute(self, statements: list[ast.ASTNode], env: Environment):
        previous_env = self.env
        try:
            self.env = env
            for stmt in statements:
                self.evaluate(stmt)
        finally:
            self.env = previous_env

    def visit_Program(self, node: ast.Program):
        for stmt in node.statements:
            self.evaluate(stmt)

    def visit_FunctionDecl(self, node: ast.FunctionDecl):
        # We store the function declaration in the environment
        self.env.define(node.name, node)

    def visit_LetDecl(self, node: ast.LetDecl):
        val = self.evaluate(node.value)
        self.env.define(node.name, val)

    def visit_IfStatement(self, node: ast.IfStatement):
        condition = self.evaluate(node.condition)
        if condition:
            self.execute(node.then_branch, Environment(self.env))
        elif node.else_branch:
            self.execute(node.else_branch, Environment(self.env))

    def visit_WhileStatement(self, node: ast.WhileStatement):
        while self.evaluate(node.condition):
            try:
                self.execute(node.body, Environment(self.env))
            except ReturnException as e:
                raise e # Propagate return

    def visit_ReturnStmt(self, node: ast.ReturnStmt):
        value = None
        if node.value is not None:
            value = self.evaluate(node.value)
        raise ReturnException(value)

    def visit_PrintStmt(self, node: ast.PrintStmt):
        val = self.evaluate(node.value)
        self.output.append(str(val))

    def visit_ExprStmt(self, node: ast.ExprStmt):
        self.evaluate(node.expr)

    def visit_BinOp(self, node: ast.BinOp):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        op = node.op

        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left / right
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return left < right
        elif op == '<=':
            return left <= right
        elif op == '>':
            return left > right
        elif op == '>=':
            return left >= right
        elif op == '=':
            # wait, assignment should be an expression or handled?
            # BinOp with '=' means assignment. left must be Ident
            if isinstance(node.left, ast.Ident):
                self.env.assign(node.left.name, right)
                return right
            else:
                raise Exception("Invalid assignment target")
        else:
            raise Exception(f"Unknown operator {op}")

    def visit_Call(self, node: ast.Call):
        func = self.env.get(node.name)
        args = [self.evaluate(arg) for arg in node.args]

        if callable(func) and not isinstance(func, ast.FunctionDecl):
            # Built-in function
            return func(*args)

        if not isinstance(func, ast.FunctionDecl):
            raise Exception(f"{node.name} is not a function")

        if len(args) != len(func.params):
            raise Exception(f"Expected {len(func.params)} arguments, got {len(args)}")

        # Create new environment for the function call
        call_env = Environment(self.global_env)
        for param_name, arg_val in zip(func.params, args):
            call_env.define(param_name, arg_val)

        try:
            self.execute(func.body, call_env)
        except ReturnException as r:
            return r.value
        
        return None

    def visit_Ident(self, node: ast.Ident):
        return self.env.get(node.name)

    def visit_Literal(self, node: ast.Literal):
        return node.value

    def visit_StringLiteral(self, node: ast.StringLiteral):
        return node.value
