from syntax import Parser

test = Parser("tests/lookup_test")

ast = test.generate()

ast.evaluate({})