import ast
import operator


OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}


def calculate(expression: str):
    expression = expression.lower().replace(" x ", " * ")
    try:
        tree = ast.parse(expression, mode="eval")

        def evaluate(node):
            if isinstance(node, ast.Expression):
                return evaluate(node.body)

            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError("Invalid value")

            if isinstance(node, ast.BinOp):
                operation = OPERATORS.get(type(node.op))

                if operation is None:
                    raise ValueError("Operator not allowed")

                return operation(
                    evaluate(node.left),
                    evaluate(node.right)
                )

            if isinstance(node, ast.UnaryOp):
                value = evaluate(node.operand)

                if isinstance(node.op, ast.USub):
                    return -value

                if isinstance(node.op, ast.UAdd):
                    return value

                raise ValueError("Operator not allowed")

            raise ValueError("Invalid expression")

        result = evaluate(tree)

        return f"The answer is {result}"

    except Exception:
        return "I couldn't calculate that expression."