import string

SCRIPT_CONFIG = {
    "NUM_INT_TOLERANCE": 10**(-4),# tolerance for floats to be converted to ints
}

def scriptError(err):
    print(err)

# removes *all* whitespace in a string
def removeWhiteSpace(s):
    clean = ""
    for c in s:
        if c not in string.whitespace:
            clean += c
    return clean

'''
Takes a string, removes whitespace, then splits into list of strings broken up
By any character in group. The character itself is not removed, but put as its
own element
'''
def splitStrByGroup(s, group):
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
                continue
        curr += s[i]
        i += 1
    spl.append(curr)
    return(spl)

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

#Environment for script to run in
class ScriptEnvironment():
    def __init__(self, constants, externals):
        # Constants - cannot be changed within scripts
        # Externals - can be changed within scripts, returned by executeStep()
        # Externals are used as the way to get output from the script
        self.locals = dict()
        self.constants = constants
        self.externals = externals
        self.instructionIndex = 0

    def loadScript(self, script):
        pass
    def evaluateExpression(self, expression):
        '''
        A legal expression takes one of two forms:
        1) variable
        2) variable operator expression
        3) expression comparator expresiion
        So we split by legal operators, and if length is one just return the
        variable, otherwise we recursively evaluate the expression and apply
        the operator
        '''
        operators = ['+', '-', '/', '*', '**', '//', '!']
        comparators = ['<', '>', '<=', '>=', '==', '!=']
        splitExpr = splitStrByGroup(expr, operators)
        splitComp = splitStrByGroup(expr, comparators)

        if len(splitComp) > 1:
            # Expression is a boolean comparison (type 3)
        elif len(splitExpr) > 1:
            # Expression is type 2
        else:
            # Expression is type 1
        
    def executeStep(self):
        pass
