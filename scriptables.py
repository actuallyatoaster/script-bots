import string

SCRIPT_CONFIG = {
    "NUM_INT_TOLERANCE": 10**(-4),# tolerance for floats to be converted to ints
}

def scriptError(err):
    print(err)

# removes excess outer lists from L
# Ex. deNest([['x']]) == 'x'; deNest([[['x', 'y']]]) == ['x', 'y']
def deNest(L):
    if isinstance(L, list) and len(L) == 1:
        return deNest(L[0])
    else: return L

# removes *all* whitespace in a string
def removeWhiteSpace(s):
    clean = ""
    for c in s:
        if c not in string.whitespace:
            clean += c
    return clean

#Returns true if expression is a comparison, false otherwise
def isBoolExpression(expression, comparators, boolOps):
    for comp in comparators:
        if comp in expression:
            return True
    for op in boolOps:
        if op in expression:
            return True
    else:
        return False

'''
Takes a string, removes whitespace, then splits into list of strings broken up
By any character in group. The character itself is not removed, but put as its
own element
'''
def splitStrByGroup(s, group):
    if s in group:
        return s
    s = removeWhiteSpace(s)
    spl = []
    curr = "" 
    i=0
    while i < len(s):
        matched = False
        for potentialMatch in reversed(sorted(group, key=len)):
            if s[i:i+len(potentialMatch)] == potentialMatch:
                spl.append(curr)
                spl.append(potentialMatch)
                i += len(potentialMatch)
                curr = ""
                matched = True
                break
        if not matched:
            curr += s[i]
            i += 1
    spl.append(curr)
    return(deNest(spl))

#returns index of first open paren in string and corresponding closing paren
def scanParenIndices(expression):
    startInd = expression.index('(')
    depth = 0
    for i in range(startInd+1, len(expression)):
        if expression[i] == '(':
            depth += 1
        elif expression[i] == ')':
            if depth == 0:
                return startInd, i
            else:
                depth -= 1
    scriptError("Unmatched parentheses")

# recursively breaks an expression into a list of strings split by parentheses
def splitParens(expression):
    spl = []

    if '(' in expression:
        if not ')' in expression: 
            scriptError("Unmatched parentheses")
        startInd, endInd = scanParenIndices(expression)
        if startInd > 0:
            spl.append(expression[0:startInd])
        spl.append(splitParens(expression[startInd + 1: endInd]))
        if endInd < len(expression) - 1:
            if '(' in expression[endInd+1:]:
                spl.extend(splitParens(expression[endInd+1:]))
            else:
                spl.append(expression[endInd+1:])
    else:
        return expression

    return spl

#recursively parse sub-expressions
def parseSubExpr(subExpr, group):
    if not isinstance(subExpr, list):
        return splitStrByGroup(subExpr, group)
    else:
        subExprList = []
        for subSubExpr in subExpr:
            subExprList.append(parseSubExpr(subSubExpr, group))
        return subExprList

#Parse an expression in string form, return parsed expression
def parseExpression(expression, group):
    spl = splitParens(expression)
    if isinstance(spl, list):
        for i in range(len(spl)):
            spl[i] = parseSubExpr(spl[i], group)
        return deNest(spl)
    else:
        return deNest(splitStrByGroup(expression, group))
    

# Generic variable type
class ScriptVariable():
    def __init__(self, type, value):
        self.type = type
        self.value = value

#T his is just a boolean
class ScriptBoolean(ScriptVariable):
    def __init__(self, value):
        super().__init__("bool", value)

'''
The Number data type behaves as a single data type for both ints and floats.
When the value is within NUM_INT_TOLERANCE of an int, the value is automatically
casted to an interger and will behave as such. Otherwise, the Number will behave
as a float.
'''
class ScriptNumber(ScriptVariable):
    def __init__(self, value):
        super().__init__("num", value)

    def assign(self, var):
        if not var.type == self.type:
            scriptErorr(f"Assignment is not of type {self.type}")
            return
        val = var.value
        if abs(val - round(val)) < SCRIPT_CONFIG["NUM_INT_TOLERANCE"]:
            val = round(val)
        self.value = val

# This is just a string.        
class ScriptString(ScriptVariable):
    def __init__(self, value):
        super().__init__("str", value)


''' TODO: Finish this
A Collection emulates a class/list/set/etc. It can contain unlimited 
'''
class ScriptCollection(ScriptVariable):
    def __init__(self):
        super().__init__("clct", dict())

    # Set the value of an element of the collection
    # If the element already exists, new value must have same type
    def assign(self, key, var):
        if key not in self.value:
            self.value[key] = var
        elif self.value[key].type == var.type:
            self.value[key] = var
        else:
            scriptError(f"Element type {self.value[key].type} different from \
            f{var.type}")

#TODO: this function needs to support floats
def stringToScriptNumber(s):
    return ScriptNumber(int(s))

#Environment for script to run in
class ScriptEnvironment():
    def __init__(self, constants = dict(), externals = dict()):
        # Constants - cannot be changed within scripts
        # Externals - can be changed within scripts, returned by executeStep()
        # Externals are used as the way to get output from the script
        self.locs = dict()
        self.constants = constants
        self.externals = externals
        self.instructionIndex = 0

    def loadScript(self, script):
        pass

    def getVariableOrConstant(self, var):
        if var.isdigit(): #TODO: support floats
            return stringToScriptNumber(var)
        elif var in self.externals:
            return self.externals[var]
        elif var in self.constants:
            return self.constants[var]
        elif var in self.locs:
            return self.locs[var]
        else:
            scriptError(f"Variable {var} is not defined")

    def evaluateBoolExpression(self, tokens):
        pass

    #This handles expression types 1 and 2
    def evaluateSubExpression(self, tokens):
        tokens = deNest(tokens)

        #Type 1
        if isinstance(tokens, list) and len(tokens) > 1:
            if len(tokens) >= 3:
                print(tokens)
                lhs = self.evaluateSubExpression(tokens[0])
                operator = tokens[1]
                rhs = self.evaluateSubExpression(tokens[2:])
                print(lhs, tokens[0], rhs, tokens[1])

                if rhs.type != lhs.type:
                    scriptError(f"Cannot use operator {operator} with " +
                        f"types {rhs.type} and {lhs.type}")
                
                if operator == '+':
                    return ScriptNumber(lhs.value + rhs.value)
                elif operator == '-':
                    return ScriptNumber(lhs.value - rhs.value)
                elif operator == '/':
                    return ScriptNumber(lhs.value / rhs.value)
                elif operator == '*':
                    return ScriptNumber(lhs.value * rhs.value)
                elif operator == '**':
                    return ScriptNumber(lhs.value** rhs.value)
                elif operator == '//':
                    return ScriptNumber(lhs.value// rhs.value)
                elif operator == '%':
                    return ScriptNumber(lhs.value % rhs.value)
                
            else: 
                scriptError("Improper expression")
                return

        #Type 2
        elif not isinstance(tokens, list):
            return self.getVariableOrConstant(tokens)
        elif len(tokens) == 1:
            return self.getVariableOrConstant(tokens[0])

    def evaluateExpression(self, expression):
        '''
        A legal expression takes one of two forms:
        1) variable
        2) variable operator expression
        3) expression comparator expresiion (bool expression)
        So we split by legal operators, and if length is one just return the
        variable, otherwise we recursively evaluate the expression and apply
        the operator
        '''
        operators = ['+', '-', '/', '*', '%', '**', '//']
        boolOperators = ['!', '&&', '||']
        comparators = ['<', '>', '<=', '>=', '==', '!=']
        #tokens = parseExpression(expression)

        if isBoolExpression(expression, comparators, boolOperators):
            parsed = deNest(parseExpression(expression, comparators + boolOperators))
            if len(parsed) == 1:
                return self.getVariableOrConstant(spl[0])
            return self.evaluateBoolExpression(parsed)
        else:
            parsed = deNest(parseExpression(expression, operators))
            if len(parsed) == 1:
                return self.getVariableOrConstant(spl[0])
            return self.evaluateSubExpression(parsed)


        
        # if len(splitComp) > 1:
        #     # Expression is a comparison (type 3)
        # elif len(splitExpr) > 1:
        #     # Expression is type 2
        # else:
        #     # Expression is type 1
        
    def executeStep(self):
        pass

if __name__ == "__main__":
    operators = ['+', '-', '/', '*', '**', '//', '!']
    x = parseExpression("((abc+d)*(c/d)+5)/t", operators)
    locs = {'abc':ScriptNumber(1), 'y':ScriptNumber(2)}
    env = ScriptEnvironment()
    env.locs = locs
