from syntax import Parser

test = Parser("traveller_freight_roller")

ast = test.generate()

ast.evaluate({})