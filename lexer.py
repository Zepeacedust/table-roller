from enum import Enum, auto

WHITESPACE = [
    " ",
    "\t",
    "\n",
]

CONTROL = [
    "(",
    ")",
    "+",
    "-",
    "*",
    "/",
    "<",
    ">",
    "=",
    ",",
    ".",
    ";",
    ":",
    "[",
    "]",
    "{",
    "}",
]

KEYWORDS = [
    "output",
    "on",
    "if",
    "while",
]


class TokenType(Enum):
    EOF = auto()
    IDENTIFIER = auto()
    WHITESPACE = auto()
    CONTROL = auto()
    CONSTANT = auto()
    DIE = auto()
    KEYWORD = auto()



class Token:
    def __init__(self, _text, _type, _pos) -> None:
        self.text = _text
        self.type = _type
        self.pos = _pos
    def __str__(self) -> str:
        return f"({self.text}, {self.type})"

class Lexer:
    def __init__(self, filename) -> None:
        self.ch:str = 'k'
        self.file = open(filename, "r")
        self.line = 0
        self.char = 0
        self.next_character()
        self.lookahead_buffer = None
    
    def tell(self):
        return (self.line, self.char)
    def next_character(self) -> str:
        out = self.ch
        self.char += 1
        if out == "\n":
            self.char = 0
            self.line += 1
        self.ch = self.file.read(1)
        return out

    def lookahead(self) -> Token:
        if self.lookahead_buffer == None:
            self.lookahead_buffer = self.next_token()
        return self.lookahead_buffer

    def expect(self, text = None, type:TokenType=None) -> Token:
        out = self.next_token()
        if type != None and out.type != type:
            raise SyntaxError(f"Expected type {type} but got {out} at line {out.pos[0]} character {out.pos[1]}")
        if text != None and out.text != text:
            raise SyntaxError(f"Expected {text} but got {out.text} at {out.pos}")
        return out

    def next_token(self) -> Token:
        if self.lookahead_buffer != None:
            out = self.lookahead_buffer
            self.lookahead_buffer = None
            return out

        while self.ch in WHITESPACE:
            self.next_character()
        
        if self.ch == "":
            return Token("EOF", TokenType.EOF, self.tell())

        if self.ch.isdigit():
            num = ""
            while self.ch.isdigit():
                num += self.next_character()
            if self.ch == "d":
                num += self.next_character()
                while self.ch.isdigit():
                    num += self.next_character()
                return Token(num, TokenType.DIE, self.tell())
            return Token(num, TokenType.CONSTANT, self.tell())

        if self.ch == '"':
            self.next_character()
            word = ""
            while self.ch != '"':
                if self.ch == "\\":
                    self.next_character()
                    escape = self.next_character()
                    if escape == "\"":
                        word += "\""
                    
                    if escape == "\n":
                        word += "\n"
                    
                    if escape =="\t":
                        word += "\t"
                    
                    if escape == "\\":
                        word += "\\"
                    
                else:
                    word += self.next_character()
                
            self.next_character()
            return Token(word, TokenType.CONSTANT, self.tell())

        if self.ch.isalpha() or self.ch == "_":
            name = ""
            while self.ch.isalnum() or self.ch == "_":
                name += self.next_character()
            if name in KEYWORDS:
                return Token(name, TokenType.KEYWORD, self.tell())
            return Token(name, TokenType.IDENTIFIER, self.tell())

        if self.ch in CONTROL:
            first = self.next_character()
            if first == "=" and self.ch == "=":
                self.next_character()
                return Token("==", TokenType.CONTROL, self.tell())
            if first == "<" and self.ch == "=":
                self.next_character()
                return Token("<=", TokenType.CONTROL, self.tell())
            if first == "<" and self.ch == "<":
                self.next_character()
                return Token("<<", TokenType.CONTROL, self.tell())
            if first == ">" and self.ch == ">":
                self.next_character()
                return Token(">>", TokenType.CONTROL, self.tell())
            if first == ">" and self.ch == "=":
                self.next_character()
                return Token(">=", TokenType.CONTROL, self.tell())
            return Token(first, TokenType.CONTROL, self.tell())