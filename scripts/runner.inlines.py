#    Copyright 2020 Valentin Dufois
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


# pyCharm trick
# noinspection PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from _stubs import *

import ast

UNARY_OPS = (ast.UAdd, ast.USub)
BINARY_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow)


def checkEquation(userInput):
    def _is_arithmetic(node):
        if isinstance(node, ast.Num):
            return True
        elif isinstance(node, ast.Expression):
            return _is_arithmetic(node.body)
        elif isinstance(node, ast.UnaryOp):
            valid_op = isinstance(node.op, UNARY_OPS)
            return valid_op and _is_arithmetic(node.operand)
        elif isinstance(node, ast.BinOp):
            valid_op = isinstance(node.op, BINARY_OPS)
            return valid_op and _is_arithmetic(node.left) and _is_arithmetic(node.right)
        else:
            return False

    try:
        if userInput.isnumeric():
            # Ignore if only one number is written
            return False

        isEquation = _is_arithmetic(ast.parse(userInput, mode='eval'))

        if not isEquation:
            return False

        result = eval(userInput)
        return '= ' + str(result)

    except (SyntaxError, ValueError):
        return False


def checkPythonExpr(userInput):
    if not userInput.startswith('>'):
        return False

    try:
        # Check if string is valid python
        cmd = userInput[1:].lstrip()

        # String is valid
        result = eval(cmd, globals().update({'me': ui.panes.current.owner}))
        if result is None:
            return False

        return '> ' + str(result)
    except:
        return False
