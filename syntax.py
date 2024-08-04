from lexer import Lexer, TokenType

from random import randint

class ASTNode:
    pass

    def evaluate(self, context):
        pass

class ASTProgram(ASTNode):
    def __init__(self) -> None:
        self.statements = []
        super().__init__()

    def evaluate(self, context):
        for statement in self.statements:
            statement.evaluate(context)

class ASTStatement(ASTNode):
    pass

class ASTAssigment(ASTNode):
    def __init__(self, identifier, expression) -> None:
        super().__init__()
        self.identifier = identifier
        self.expression = expression
    
    def evaluate(self, context):
        context[self.identifier] = self.expression.evaluate(context)

class ASTOutput(ASTNode):
    def __init__(self, expression) -> None:
        super().__init__()
        self.expreession = expression
    
    def evaluate(self, context):
        print(self.expreession.evaluate(context))

class ASTExpression(ASTNode):
    pass

class ASTIdentifier(ASTNode):
    def __init__(self, identifier) -> None:
        super().__init__()
        self.identifier = identifier


    def evaluate(self, context):
        return context[self.identifier]

class ASTBinaryOperator(ASTNode):
    def __init__(self, operator, lhs, rhs) -> None:
        super().__init__()
        self.lhs = lhs
        self.operator = operator
        self.rhs = rhs
    
    def evaluate(self, context):
        lhs = self.lhs.evaluate(context)


        rhs = self.rhs.evaluate(context)
        if self.operator == "==":
            return int(lhs == rhs)
        if self.operator == "<=":
            return int(lhs <= rhs)
        if self.operator == ">=":
            return int(lhs >= rhs)
        if self.operator == "<":
            return int(lhs<rhs)
        if self.operator == ">":
            return int(lhs>rhs)
        
        if self.operator == "+":
            return lhs+rhs
        if self.operator == "-":
            return lhs-rhs
        if self.operator == "*":
            return lhs*rhs
        if self.operator == "/":
            return lhs/rhs

class ASTUnaryOperator(ASTNode):
    def __init__(self, operator, value) -> None:
        super().__init__()
        self.opeator = operator
        self.value = value
    
    def evaluate(self, context):
        if self.opeator == "-":
            return -self.value.evaluate(context)

class ASTConstant(ASTNode):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value

    def evaluate(self, context):
        return self.value
    
class ASTLookup(ASTNode):
    def __init__(self, value, table) -> None:
        super().__init__()
        self.value = value
        self.table = table

    def evaluate(self, context):
        key = self.value.evaluate(context)
        table = self.table.evaluate(context)
        return table[key].evaluate(context)
    
class ASTDie(ASTNode):
    def __init__(self, number, size) -> None:
        super().__init__()
        self.number = number
        self.size = size

    
    def evaluate(self, context):
        acc = 0
        for x in range(self.number):
            acc += randint(1,self.size)
        return acc
    
class ASTTable(ASTNode):
    def __init__(self, entries) -> None:
        super().__init__()
        self.entries= entries
    
    def evaluate(self, context):
        return self.entries

class ASTIf(ASTNode):
    def __init__(self, cond, statements) -> None:
        super().__init__()
        self.cond = cond
        self.statements = statements
    
    def evaluate(self, context):
        if self.cond.evaluate(context):
            for statement in self.statements:
                statement.evaluate(context)

class ASTWhile(ASTNode):
    def __init__(self, cond, statements) -> None:
        super().__init__()
        self.cond = cond
        self.statements = statements
    
    def evaluate(self, context):
        while self.cond.evaluate(context):
            for statement in self.statements:
                statement.evaluate(context)


class Parser:
    def __init__(self, filename) -> None:
        self.lexer = Lexer(filename)
    
    def generate(self):
        program = ASTProgram()
        while self.lexer.lookahead().type != TokenType.EOF:
            program.statements.append(self.statement())
        self.lexer.expect(type=TokenType.EOF)
        return program


    def statement(self):
        if self.lexer.lookahead().type == TokenType.IDENTIFIER:
            out = self.assignmentStatement()
        elif self.lexer.lookahead().text == "output":
            self.lexer.expect(text="output")
            expression = self.expression()
            out = ASTOutput(expression) 
        elif self.lexer.lookahead().text == "while":
            return self.while_statement()
        elif self.lexer.lookahead().text == "if":
            return self.if_statement()
        self.lexer.expect(type=TokenType.CONTROL, text=";")
        return out
    
    def if_statement(self):
        self.lexer.expect(text="if")
        self.lexer.expect(text="(")
        cond = self.expression()
        self.lexer.expect(text=")")
        self.lexer.expect(text="{")
        statements = self.block()
        self.lexer.expect(text="}")
        return ASTIf(cond, statements)

    def while_statement(self):
        self.lexer.expect(text="while")
        self.lexer.expect(text="(")
        cond = self.expression()
        self.lexer.expect(text=")")
        self.lexer.expect(text="{")
        statements = self.block()
        self.lexer.expect(text="}")
        return ASTWhile(cond, statements)

    def block(self):
        statements = []

        while self.lexer.lookahead().text != "}":
            statements.append(self.statement())
        
        return statements
    
    def assignmentStatement(self):
        identifier = self.lexer.expect(type=TokenType.IDENTIFIER)
        self.lexer.expect(text="=")
        expression = self.expression()
        return ASTAssigment(identifier.text, expression)

    def table(self):
        self.lexer.expect(text="[")
        entries = {}
        while self.lexer.lookahead().type == TokenType.CONSTANT:
            key = self.lexer.expect(type=TokenType.CONSTANT)
            self.lexer.expect(text=":")
            
            entries[int(key.text)] = self.expression()

            # if self.lexer.lookahead().type == TokenType.CONSTANT:
            #     value = self.lexer.expect(type=TokenType.CONSTANT)
            #     entries[int(key.text)] = ASTConstant(value.text)

            # elif self.lexer.lookahead().type == TokenType.DIE:
            #     value = self.lexer.expect(type=TokenType.DIE)
            #     parts = value.text.split("d")
            #     entries[int(key.text)] = ASTDie(int(parts[0]), int(parts[1]))
            
            self.lexer.expect(text=",")

        self.lexer.expect(text="]")
        return ASTTable(entries)
        

    def expression(self):
        first = self.conditional()
        if self.lexer.lookahead().text == "on":
            self.lexer.expect("on")
            if self.lexer.lookahead().type == TokenType.IDENTIFIER:
                table = ASTIdentifier(self.lexer.next_token().text)
            else:
                table = self.table()
            first = ASTLookup(first, table)
            
        return first
    
    def conditional(self):
        first = self.sum()
        while self.lexer.lookahead().text in ["==", ">=", "<=", "<", ">"]:
            operator = self.lexer.next_token()
            right = self.sum()
            first = ASTBinaryOperator(operator.text, first, right)
        return first

    def sum(self):
        if self.lexer.lookahead().text == "[":
            return self.table()

        first = self.product()
        while self.lexer.lookahead().text in ["+", "-"]:
            operator = self.lexer.next_token()
            right = self.product()
            first = ASTBinaryOperator(operator.text, first, right)
        return first

    def product(self):
        first = self.unary()
        while self.lexer.lookahead().text in ["*", "/"]:
            operator = self.lexer.next_token()
            right = self.unary()
            first = ASTBinaryOperator(operator.text, first, right)
        return first

    def unary(self):
        first = self.lexer.next_token()
        if first.type == TokenType.CONSTANT:
            if first.text.isnumeric():
                return ASTConstant(int(first.text))
            return ASTConstant(first.text)
        
        if first.type == TokenType.IDENTIFIER:
            return ASTIdentifier(first.text)

        if first.type == TokenType.DIE:
            parts = first.text.split("d")
            return ASTDie(int(parts[0]), int(parts[1]))

        if first.type == TokenType.CONTROL and first.text == "(":
            subexpr = self.expression()
            self.lexer.expect(text=")")
            return subexpr
        
        if first.text == "-":
            return ASTUnaryOperator("-", self.unary())
