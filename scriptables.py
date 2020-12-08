'''
This file contains the BotScript interpreter and all related classes and
functions. The core of the file is the ScriptEnvironment class, wherein scripts
and their variables are stored, and scripts are parsed and run.
'''

import string
import math
import random

#Some configuration for the script environment
SCRIPT_CONFIG = {
    "NUM_INT_TOLERANCE": 10**(-6),# tolerance for floats to be converted to ints
}

#Error type used for errors within scripts
class ScriptError(Exception):
    pass

def scriptError(err):
    print(err)
    raise ScriptError

def scriptLog(msg):
    print(msg) #temp!!!!!

################################################################################
### Helper functions for expression parsing                                  ###
################################################################################

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

#Returns true if expression is a boolean expression, false otherwise
def isBoolExpression(expression, comparators, boolOps):
    for comp in comparators:
        if comp in expression:
            return True
    for op in boolOps:
        if op in expression:
            return True
    return False

#Basically the same as isBoolExpression
def isComparison(expression, comparators):
    for comp in comparators:
        if comp in expression:
            return True
    return False

#Finds the first element of group that exists in L and returns its index in L
def findGroupIndex(L, group):
    for i in group:
        if i in L:
            return L.index(i)
    return -1 #return -1 if not found

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
                if curr != "": spl.append(curr)
                spl.append(potentialMatch)
                i += len(potentialMatch)
                curr = ""
                matched = True
                break
        if not matched:
            curr += s[i]
            i += 1
    if curr != "": spl.append(curr)
    return(spl)

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

#generalization of scanParenIndices for line prefixes
#Returns index of closing prefex that corresponds to opening prefix
#at given infex
def scanPrefixIndex(lines, index, startPrefix, endPrefix, reverse = False):
    l = None  
    if reverse:
        l = len(lines)
        index = l - index
        lines = reversed(lines)
        startPrefix, endPrefix = endPrefix, startPrefix
    if not lines[index].startswith(startPrefix):
        scriptError("This really shouldn't happen")
        return
    depth = 0
    for i in range(index+1, len(lines)):
        if lines[i].startswith(startPrefix):
            depth +=1
        elif lines[i].startswith(endPrefix):
            if depth == 0:
                return i if not reverse else l-i
            else:
                depth -= 1
    scriptError(f"Bad syntax: {startPrefix} on line {index} does not have"+
                f" a matching {endPrefix}")

#Now entering the recursion zone😈...
# recursively breaks an expression into a list of strings split by parentheses
def splitParens(expression):
    spl = []

    if '(' in expression:
        if not ')' in expression: 
            scriptError("Unmatched parentheses")
            return
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
# def parseSubExpr(subExpr, group):
#     if not isinstance(subExpr, list):
#         return splitStrByGroup(subExpr, group)
#     else:
#         subExprList = []
#         for subSubExpr in subExpr:
#             subExprList.append(parseSubExpr(subSubExpr, group))
#         return subExprList

def parseSubExpr(subExpr, group):
    if not isinstance(subExpr, list):
        return splitStrByGroup(subExpr, group)
    else:
        subExprList = []
        for subSubExpr in subExpr:
            parsedSub = parseSubExpr(subSubExpr, group)
            #Case where first or last is an operator
            if isinstance(parsedSub, list) and (parsedSub[0] in group or 
                                                parsedSub[-1] in group):
                subExprList.extend(parsedSub)
            #otherwise
            else:
                subExprList.append(parsedSub)
        return subExprList


#Parse an expression in string form, return parsed expression
def parseExpression(expression, group):
    spl = splitParens(expression)
    if isinstance(spl, list):
        i = 0
        while i <len(spl):
            parsedSub = parseSubExpr(spl[i], group)
            #Case where the parsed expression only has one element
            if len(parsedSub) == 1 or parsedSub in group:
                spl[i] = parsedSub
                i += 1
            #Case where the last character in the sub expr is an operator
            elif parsedSub[-1] in group and parsedSub[0] not in group:
                spl[i] = parsedSub[0:-1]
                spl.insert(i+1, parsedSub[-1])
                i += 2
            #Case where first character is an operators
            elif parsedSub[0] in group and parsedSub[-1] not in group:
                spl[i] = parsedSub[0]
                spl.insert(i+1, parsedSub[1:])
                i += 2
            #Case where first and last characters are both operators
            elif parsedSub[0] in group and parsedSub[-1] in group:
                spl[i] = parsedSub[0]
                spl.insert(i+1, parsedSub[1:-1])
                spl.insert(i+2, parsedSub[-1])
                i += 3
            else:
                spl[i] = parseSubExpr(spl[i], group)
                i += 1
        return spl
    else:
        return splitStrByGroup(expression, group)
    
#Takes a list of tokens that has at least one '!'. The '!' element is merged
#With the next element in the list
#ex. ['True', '&&', '!', 'False'] --> ['True', '&&', ['!', 'False']]
# ['True' '&&', '!', ['False', '&&', 'True]]
# --> ['True' '&&', ['!', ['False', '&&', 'True]]]
#NOTE: this function feels like a recipe for alias hell if used incorrectly
def bangPreprocessor(tokens):
    new = []
    first = -1
    i = 0
    while i < len(tokens):
        if tokens[i] == '!':
            new.append([tokens[i], tokens[i+1]])
            if first == -1: first = i
            i +=2
        else:
            new.append(tokens[i])
            i+=1
    #Parsing things with '!' can create a few artifacts that we need to remove
    if isinstance(new[0], list) and first != 0:
        new = new[0] + new[1:]
    i = 0
    while i < len(new):
        if new[i] == []:
            new.pop(i)
        else:
            i += 1

    return new

################################################################################
### Script data types and environment                                        ###
################################################################################

# Generic variable type
class ScriptVariable():
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def assign(self, var):
        if not var.type == self.type:
            scriptError(f"Assignment is not of type {self.type}")
            return
        else:
            self.value = var.value


# This is just a boolean
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
        self.assign(self)

    def assign(self, var):
        if not var.type == self.type:
            scriptError(f"Assignment is not of type {self.type}")
            return
        val = var.value
        if abs(val - round(val)) < SCRIPT_CONFIG["NUM_INT_TOLERANCE"]:
            val = round(val)
        self.value = val

# This is just a string.        
class ScriptString(ScriptVariable):
    def __init__(self, value):
        super().__init__("str", value)


#TODO: Delete this class
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

#Convert a string to a ScriptNumber
def stringToScriptNumber(s):
    if '.' in s:
        return ScriptNumber(float(s))
    else:
        return ScriptNumber(int(s))

#Environment for script to run in
class ScriptEnvironment():
    def __init__(self, script = "", constants = None, externals = None):
        # Constants - cannot be changed within scripts
        # Externals - can be changed within scripts, returned by executeStep()
        # Externals are used as the way to get output from the script
        self.locs = dict()
        if constants == None:
            self.constants = dict()
        else: self.constants = constants
        if externals == None:
            self.externals = dict()
        else: self.externals = externals
        self.instructionIndex = 0
        self.lines = []
        self.parseCache = dict()
        if script:
            for line in script.split('\n'):
                line = removeWhiteSpace(line)
                if '#' in line:
                    line = line[:line.find('#')]
                if line !="":
                    self.lines.append(line)

    #This function takes a constant or variable and returns its value
    #Also handles the following builtin functions: cos, sin, tan, arccos,
    #arcsin, arctan, abs, floor, ceil, round
    def getVariableOrConstant(self, var):
        #Just a single variable or constant to return value of
        if var.isdigit() or (
            var.count('.') == 1 and
            var.translate({ord('.'):None}).isdigit() #Checks if name exclusing "." is all numbers
        ):
            return stringToScriptNumber(var)
        elif var == "True":
            return ScriptBoolean(True)
        elif var == "False":
            return ScriptBoolean(False)
        elif var in self.externals:
            return self.externals[var]
        elif var in self.constants:
            return self.constants[var]
        elif var in self.locs:
            return self.locs[var]
        else:
            scriptError(f"Variable {var} is not defined")

    #Set a variable            
    def setVariable(self, var, value):
        varTypes = ["num", "str", "bool"]
        #Case where creating a new variable
        for varType in varTypes:
            if var.startswith(varType):
                varName = var[len(varType):]
                if ((varName in self.locs or varName in self.constants or
                    varName in self.externals)):
                    scriptError(f"Variable {varName} already exists")
                    return
                elif value.type != varType:
                    scriptError(f"Assignment is not of type {varType}")
                    return
                else:
                    self.locs[varName] = value
                    return
        #Case where assigning a new variable:
        if var in self.locs:
            self.locs[var].assign(value)
        elif var in self.externals:
            self.externals[var].assign(value)
        elif var in self.constants:
            scriptError(f"Cant assign {var} -- is a constant")
        else:
            scriptError(f"Cant assign {var} -- doesn't exist")

    # Recursively evaluates parsed boolean expressions
    def evaluateBoolExpression(self, tokens, comparators):
        tokens  = deNest(tokens)
        
        if isinstance(tokens, list):
            #Special case for ! operator
            if len(tokens) == 2:
                if deNest(tokens[0]) != "!":
                    scriptError("Improper expression")
                    return
                rhs = self.evaluateBoolExpression(tokens[1], comparators)
                return ScriptBoolean(not rhs.value)
            elif len(tokens) > 2 and "!" in tokens:
                #This is really janky, i know 
                tokens = bangPreprocessor(tokens)
                return self.evaluateBoolExpression(tokens, comparators)
                
            elif len(tokens) == 1:
                return self.getVariableOrConstant(tokens[0])
            
            #Numerical Comparisons
            elif isComparison(tokens, comparators):

                compIndex = findGroupIndex(tokens, comparators)
                if compIndex == 0 or compIndex == len(tokens) -1:
                    scriptError("Improper expression")
                    return

                lhs = self.evaluateSubExpression(tokens[0:compIndex])
                comparator = deNest(tokens[compIndex])
                rhs = self.evaluateSubExpression(tokens[compIndex+1:])
                if comparator == '<':
                    return ScriptBoolean(lhs.value < rhs.value)
                elif comparator == '>':
                    return ScriptBoolean(lhs.value > rhs.value)
                elif comparator == '<=':
                    return ScriptBoolean(lhs.value <= rhs.value)
                elif comparator == '>=':
                    return ScriptBoolean(lhs.value >= rhs.value)
                elif comparator == '==':
                    return ScriptBoolean(lhs.value == rhs.value)
                elif comparator == '!=':
                    return ScriptBoolean(lhs.value != rhs.value)

            #Boolean operations  
            else:
                lhs = self.evaluateBoolExpression(tokens[0], comparators)
                operator = deNest(tokens[1])
                rhs = self.evaluateBoolExpression(tokens[2:], comparators)
                if operator  == '&&':
                    return ScriptBoolean(lhs.value and rhs.value)
                elif operator  == '||':
                    return ScriptBoolean(lhs.value or rhs.value)
                elif operator  == '&!':
                    return ScriptBoolean(lhs.value and (not rhs.value))
                elif operator  == '|!':
                    return ScriptBoolean(lhs.value or (not rhs.value))
        #Constant/variable
        else:
            return self.getVariableOrConstant(tokens)
    
    #Evaluate a builtin function f on ScriptNumber rhs
    def evalBuiltin(self, f, rhs):
        builtins = {"cos", "sin", "tan", "arccos", "arcsin", "arctan", "abs",
                    "floor", "ceil", "round", "rand"}
        
        if f not in builtins:
            scriptError(f"Undefined function: {f}")
            return
        elif f == 'cos':
            return ScriptNumber(math.cos(rhs.value))
        elif f == 'sin':
            return ScriptNumber(math.sin(rhs.value))
        elif f == 'tan':
            return ScriptNumber(math.tan(rhs.value))
        elif f == 'arccos':
            return ScriptNumber(math.acos(rhs.value))
        elif f == 'arcsin':
            return ScriptNumber(math.asin(rhs.value))
        elif f == 'arctan':
            return ScriptNumber(math.atan(rhs.value))
        elif f == 'abs':
            return ScriptNumber(abs(rhs.value))
        elif f == 'floor':
            return ScriptNumber(math.floor(rhs.value))
        elif f == 'ceil':
            return ScriptNumber(math.ceil(rhs.value))
        elif f == 'round':
            return ScriptNumber(round(rhs.value))
        elif f == 'rand':
            return ScriptNumber(random.randrange(rhs.value))

    #This recursively evaluates parsed numerical expressions
    def evaluateSubExpression(self, tokens):
        tokens = deNest(tokens)
        #expression with some kind of operation
        if isinstance(tokens, list) and len(tokens) > 1:
            #Case for negative numbers
            if deNest(tokens[0]) == "-":
                # Having an operator that can take a variable number of args
                # opens a huge can of worms in terms of parsing
                scriptError("BotScript does not support writing negatives"+
                " with '-'. Please use the negative operator '^' or '0-<num>'." )
            if tokens[0] == "^":
                rhs = self.evaluateSubExpression(tokens[1:])
                if rhs.type != "num":
                    scriptError(f"Cannot make type {rhs.type} negative")
                else:
                    return ScriptNumber(-1*rhs.value)
            elif len(tokens) >= 3:
                operator = deNest(tokens[1])
                rhs = self.evaluateSubExpression(tokens[2:])
                #Using a builtin function
                if operator == ':':
                    rhs = self.evaluateSubExpression(tokens[2:])
                    return self.evalBuiltin(deNest(tokens[0]), rhs)
                lhs = self.evaluateSubExpression(tokens[0])

                return self.evalOperator(lhs, operator, rhs)
                
            else: 
                scriptError("Improper expression")
                return

        #get variable or constant value
        elif not isinstance(tokens, list):
            return self.getVariableOrConstant(tokens)
        elif len(tokens) == 1:
            return self.getVariableOrConstant(tokens[0])

    def evalOperator(self, lhs, operator, rhs):
        if rhs.type != lhs.type:
            scriptError(f"Cannot use operator {operator} with " +
                f"types {rhs.type} and {lhs.type}")
        if operator == "^":
            scriptError("Operator '^' cannot take two arguments")
        elif operator == '+':
            return ScriptNumber(lhs.value + rhs.value)
        elif operator == '-':
            return ScriptNumber(lhs.value - rhs.value)
        elif operator == '/':
            if rhs.value == 0:
                scriptError("Dividing by zero!")
                return
            return ScriptNumber(lhs.value / rhs.value)
        elif operator == '*':
            return ScriptNumber(lhs.value * rhs.value)
        elif operator == '**':
            return ScriptNumber(lhs.value** rhs.value)
        elif operator == '//':
            if rhs.value == 0:
                scriptError("Dividing by zero!")
                return
            return ScriptNumber(lhs.value// rhs.value)
        elif operator == '%':
            return ScriptNumber(lhs.value % rhs.value)
        scriptError(f"Unknown operator: {operator}")
    def evaluateExpression(self, expression):

        operators = ['+', '-', '/', '*', '%', '**', '//', ':', '^']
        boolOperators = ['&&', '||', '&!', '|!', '!']
        comparators = ['<', '>', '<=', '>=', '==', '!=']

        if isBoolExpression(expression, comparators, boolOperators):
            #Evaluate as a boolean expression
            if expression in self.parseCache:
                parsed = self.parseCache[expression]
            else:
                parsed = deNest(parseExpression(expression, comparators + boolOperators + operators))
                self.parseCache[expression] = parsed
            
            if len(parsed) == 1:
                return self.getVariableOrConstant(parsed[0])
            return self.evaluateBoolExpression(parsed, comparators)
        else:
            #Evaluate as a numerical expression
            if expression in self.parseCache:
                parsed = self.parseCache[expression]
            else:
                parsed = deNest(parseExpression(expression, operators))
                self.parseCache[expression] = parsed
            
            if len(parsed) == 1: #TODO: i think this and corresponding in bool expression can be removed
                return self.getVariableOrConstant(parsed[0])
            return self.evaluateSubExpression(parsed)

    #This originally a bit of a hack for debugging but it works perfectly
    #Executes a whole script and return local and external vars at completion
    def executeAll(self):
        while self.executeNext(): pass
        self.instructionIndex = 0
        return self.locs, self.externals

    #Execute the next line
    def executeNext(self):
        try:
            #print(self.lines[self.instructionIndex])
            self.instructionIndex = self.executeStep(self.lines[self.instructionIndex],
                                    self.instructionIndex)
            #input()
            if self.instructionIndex >= len(self.lines):
                return None
            else:
                return self.locs, self.externals
        except ScriptError:
            scriptError(f"Error on line {self.instructionIndex}: {self.lines[self.instructionIndex]}")
            return

    #Execute a given line, return the new instructionIndex
    def executeStep(self, step, opIndex, verbose=False):
        step = removeWhiteSpace(step)
        comparators = ['<', '>', '<=', '>=', '==', '!='] #used to check '=' isn't = '==' or '>=' etc.
        assignmentSplit = splitStrByGroup(step, comparators + ["="])
        
        #Line is assigning a variable
        if '=' in assignmentSplit:
            if assignmentSplit[1] != '=' or assignmentSplit.count("=") >1:
                scriptError("Improper assignment")
                return
            else:
                opInd = step.find('=')
                if opInd == -1:
                    scriptError("Improper assignment")
                    return
                var = step[0:opInd]
                rhs = self.evaluateExpression(step[opInd+1:])
                self.setVariable(var, rhs)
                if verbose: scriptLog(rhs.value)
        #Line is printing to log
        elif step[0:4] == "log:":
            scriptLog(self.evaluateExpression(step[4:]).value)
        #Line is beggining of if statement
        elif step[0:2] == "if":
            if not self.evaluateExpression(step[2:]).value:
                endIfIndex = scanPrefixIndex(self.lines, opIndex, 'if', 'endif')
                #print(self.lines[endIfIndex])
                if self.lines[endIfIndex+1] == 'else':
                    return endIfIndex + 2
                else:
                    return endIfIndex
            return opIndex + 1
        elif step[0:5] == "else": #only actually reached when the if statement evals to true
            if self.lines[opIndex-1][:5] != "endif":
                scriptError("'else' does not follow endif")
                return
            else:
                endElse = scanPrefixIndex(self.lines, opIndex, 'else', 'endelse')
                return endElse
        #None of the above, just expression, print for debugging purposes
        elif verbose and step != "":
            scriptLog(self.evaluateExpression(step).value)

        return opIndex + 1


#################### Everything below here is for debugging ####################

if __name__ == "__main__":
    #Override the scriptLog function to print to command line
    def scriptLog(msg):
        print(msg)

    #Basic repl for testing
    def repl(env):
        inp = ""
        while inp != "exit":
            try:
                inp = input("S>> ")
                if inp != "exit":
                    env.executeStep(inp, 0, verbose=True)
            except ScriptError:
                pass
            except Exception as err:
                print(f"Unknown Error: {err}")
    #Setup some helpful variables for debugging
    operators = ['+', '-', '/', '*', '%', '**', '//', ':', '^']
    boolOperators = ['&&', '||', '&!', '|!', '!']
    comparators = ['<', '>', '<=', '>=', '==', '!=']        
    #Setup an empty script environment and start repl
    env = ScriptEnvironment()
    repl(env)
