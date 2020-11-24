'''
Some tests to make sure all the scripting stuff is behaving properly.
This won't be included in the final project.
'''

from scriptables import *

class Test():
    def __init__(self, script, const, ext, extOutExpected):
        self.script = script
        self.env = ScriptEnvironment(script=script, constants=const, externals=ext)
        self.expected = extOutExpected

def varsMatch(vars1, vars2):
    for var in vars1:
        if var not in vars2:
            return False
        if vars1[var].value != vars2[var].value:
            return False
    return True

def testAll(tests):
    #A few expressions that have caused bugs in the past
    testExpressions = [
        ("((1+5)**2)+((1+5)**2)",72),
        ("(True && False) || !True", False),
        ("(3+1)/2", 2),
        ("^(3+1)", -4),
        ("^(4+2)", -6),
        ("^(^3+1)", 4)
    ]
    print("Testing sample scripts... ", end="")

    #test full scripts
    for test in tests:
        locs, ext = test.env.executeAll()
        # for e in ext:
        #     print(f"{e}: {ext[e].value}")
        assert(varsMatch(test.expected, ext))

    #test expressions
    env = ScriptEnvironment()
    for expr, result in testExpressions:
        assert(env.evaluateExpression(expr).value == result)

    print("Passed!")

if __name__ == "__main__":
    tests = []
    ########### Test 1 - Numerical variable assignment
    const = dict()
    ext = {"out":ScriptNumber(0), "b":ScriptBoolean(False)}
    testStr = ''''
    num a = 52
    out = a
    '''   
    out = {"out":ScriptNumber(52), "b":ScriptBoolean(False)}
    tests.append(Test(testStr, const, ext, out))

    ########### Test 2 - Numerical variable assignment
    const = dict()
    ext = {"out":ScriptNumber(30), "b":ScriptBoolean(False)}
    testStr = ''''
    num a = 52
    out = a + out
    b = True
    ''' 
    out = {"out":ScriptNumber(82), "b":ScriptBoolean(True)}
    tests.append(Test(testStr, const, ext, out))

    ########### Test 3 - Conditionals
    const = dict()
    ext = {"out":ScriptNumber(30), "b":ScriptBoolean(False), "a":ScriptNumber(42)}
    testStr = '''
    if 1 == 1
        if 1 < 2
            out = 0
        endif
        if 2<1
            out=-1
        endif
    endif

    if 1 == 2
        b = True
    endif

    if 1!=2
        a = a+1
    endif

    ''' 
    out = {"out":ScriptNumber(0), "b":ScriptBoolean(False), "a":ScriptNumber(43)}
    tests.append(Test(testStr, const, ext, out))

    ########### Test 4 - Boolean operations and conditionals
    const = dict()
    ext = {"out":ScriptNumber(30), "b":ScriptBoolean(False), "a":ScriptNumber(42)}
    testStr = '''
    num ab = out - 25
    if ab < out
        out = out + ab
    endif

    bool test = (ab < out) && True
    bool other = True && False

    if other
        out = 1000000
    endif

    if test
        if test
            b = test
        endif
        a = 10
    endif

    ''' 
    out = {"out":ScriptNumber(35), "b":ScriptBoolean(True), "a":ScriptNumber(10)}
    tests.append(Test(testStr, const, ext, out))
    ############ Else statements
    const = dict()
    ext = {"out":ScriptNumber(30), "b":ScriptBoolean(False), "a":ScriptNumber(42)}
    testStr = '''
    if b
        out=0
    endif
    else
        out=1
        if b
            a = 0
        endif
        else
            a=50
        endelse
    endelse

    ''' 
    out = {"out":ScriptNumber(1), "b":ScriptBoolean(False), "a":ScriptNumber(50)}
    tests.append(Test(testStr, const, ext, out))
    ############ Else statements
    const = dict()
    ext = {"out":ScriptNumber(30), "b":ScriptBoolean(False), "a":ScriptNumber(42)}
    testStr = '''
    if b
        out=0
    endif
    else
        out=1
        if !b
            a = 0
        endif
        else
            a=50
        endelse
    endelse

    ''' 
    out = {"out":ScriptNumber(1), "b":ScriptBoolean(False), "a":ScriptNumber(0)}
    tests.append(Test(testStr, const, ext, out))


    testAll(tests)
