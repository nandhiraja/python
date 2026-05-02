from lexer import Lexer, Token
import ast_nodes as ast

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def current_token(self) -> Token:
        return self.tokens[self.pos]

    def peek_token(self) -> Token:
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return self.tokens[-1]

    def consume(self, expected_type: str = None) -> Token:
        token = self.current_token()
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {token.type} '{token.value}' at token pos {self.pos}")
        self.pos += 1
        return token

    def match(self, token_type: str) -> bool:
        if self.current_token().type == token_type:
            self.consume()
            return True
        return False

    def parse(self) -> ast.Program:
        statements = []
        while self.current_token().type != Lexer.EOF:
            statements.append(self.parse_statement())
        return ast.Program(statements)

    def parse_statement() -> ast.ASTNode:
        pass

    def parse_statement(self) -> ast.ASTNode:
        token_type = self.current_token().type
        if token_type == Lexer.FN:
            return self.parse_function_decl()
        elif token_type == Lexer.LET:
            return self.parse_let_decl()
        elif token_type == Lexer.IF:
            return self.parse_if_statement()
        elif token_type == Lexer.WHILE:
            return self.parse_while_statement()
        elif token_type == Lexer.RETURN:
            return self.parse_return_statement()
        elif token_type == Lexer.PRINT:
            return self.parse_print_statement()
        else:
            expr = self.parse_expression()
            return ast.ExprStmt(expr)

    def parse_block(self) -> list[ast.ASTNode]:
        self.consume(Lexer.LBRACE)
        statements = []
        while self.current_token().type != Lexer.RBRACE and self.current_token().type != Lexer.EOF:
            statements.append(self.parse_statement())
        self.consume(Lexer.RBRACE)
        return statements

    def parse_function_decl(self) -> ast.FunctionDecl:
        self.consume(Lexer.FN)
        name = self.consume(Lexer.IDENT).value
        self.consume(Lexer.LPAREN)
        params = []
        if self.current_token().type != Lexer.RPAREN:
            params.append(self.consume(Lexer.IDENT).value)
            while self.match(Lexer.COMMA):
                params.append(self.consume(Lexer.IDENT).value)
        self.consume(Lexer.RPAREN)
        body = self.parse_block()
        return ast.FunctionDecl(name, params, body)

    def parse_let_decl(self) -> ast.LetDecl:
        self.consume(Lexer.LET)
        name = self.consume(Lexer.IDENT).value
        self.consume(Lexer.ASSIGN)
        value = self.parse_expression()
        return ast.LetDecl(name, value)

    def parse_if_statement(self) -> ast.IfStatement:
        self.consume(Lexer.IF)
        condition = self.parse_expression()
        then_branch = self.parse_block()
        else_branch = None
        if self.match(Lexer.ELSE):
            else_branch = self.parse_block()
        return ast.IfStatement(condition, then_branch, else_branch)

    def parse_while_statement(self) -> ast.WhileStatement:
        self.consume(Lexer.WHILE)
        condition = self.parse_expression()
        body = self.parse_block()
        return ast.WhileStatement(condition, body)

    def parse_return_statement(self) -> ast.ReturnStmt:
        self.consume(Lexer.RETURN)
        # Check if return is empty
        if self.current_token().type in [Lexer.RBRACE, Lexer.EOF]:
            return ast.ReturnStmt(None)
        value = self.parse_expression()
        return ast.ReturnStmt(value)

    def parse_print_statement(self) -> ast.PrintStmt:
        self.consume(Lexer.PRINT)
        self.consume(Lexer.LPAREN)
        value = self.parse_expression()
        self.consume(Lexer.RPAREN)
        return ast.PrintStmt(value)

    def parse_expression(self) -> ast.ASTNode:
        return self.parse_equality()

    def parse_equality(self) -> ast.ASTNode:
        expr = self.parse_relational()
        while self.current_token().type in [Lexer.EQ, Lexer.NEQ]:
            op = self.consume().value
            right = self.parse_relational()
            expr = ast.BinOp(op, expr, right)
        return expr

    def parse_relational(self) -> ast.ASTNode:
        expr = self.parse_additive()
        while self.current_token().type in [Lexer.LT, Lexer.LTE, Lexer.GT, Lexer.GTE]:
            op = self.consume().value
            right = self.parse_additive()
            expr = ast.BinOp(op, expr, right)
        return expr

    def parse_additive(self) -> ast.ASTNode:
        expr = self.parse_multiplicative()
        while self.current_token().type in [Lexer.PLUS, Lexer.MINUS]:
            op = self.consume().value
            right = self.parse_multiplicative()
            expr = ast.BinOp(op, expr, right)
        return expr

    def parse_multiplicative(self) -> ast.ASTNode:
        expr = self.parse_primary()
        while self.current_token().type in [Lexer.STAR, Lexer.SLASH]:
            op = self.consume().value
            right = self.parse_primary()
            expr = ast.BinOp(op, expr, right)
        return expr

    def parse_primary(self) -> ast.ASTNode:
        token = self.consume()
        if token.type == Lexer.INT:
            return ast.Literal(token.value)
        elif token.type == Lexer.STRING:
            return ast.StringLiteral(token.value)
        elif token.type == Lexer.IDENT:
            if self.current_token().type == Lexer.LPAREN:
                # Function call
                self.consume(Lexer.LPAREN)
                args = []
                if self.current_token().type != Lexer.RPAREN:
                    args.append(self.parse_expression())
                    while self.match(Lexer.COMMA):
                        args.append(self.parse_expression())
                self.consume(Lexer.RPAREN)
                return ast.Call(token.value, args)
            return ast.Ident(token.value)
        elif token.type == Lexer.LPAREN:
            expr = self.parse_expression()
            self.consume(Lexer.RPAREN)
            return expr
        else:
            raise SyntaxError(f"Unexpected token in expression: {token.type} '{token.value}'")
