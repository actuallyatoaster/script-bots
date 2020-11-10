from scriptables import *

class Test():
    def __init__(self, script, const, ext, extOutExpected):
        self.script = script
        self.env = ScriptEnvironment(script=script, constants=const, externals=ext)
        self.expected = extOutExpected

def testAll():
    for test in botScriptTests:
        pass

if __name__ == "__main__":
    tests = []

    const = dict()
    ext = {"out":ScriptNumber(0), "b":ScriptBoolean(False)}
    testStr = ''''
    num a = 52
    out = a
    '''   
    out = {"out":ScriptNumber(52), "b":ScriptBoolean(False)}
    tests.append(Test(testStr, const, ext, out))

    const = dict()
    ext = {"out":ScriptNumber(30), "b":ScriptBoolean(False)}
    testStr = ''''
    num a = 52
    out = a + out
    b = True
    ''' 
    out = {"out":ScriptNumber(82), "b":ScriptBoolean(True)}
    tests.append(Test(testStr, const, ext, out))

    const = dict()
    ext = {"out":ScriptNumber(30), "b":ScriptBoolean(False), "a":ScriptNumber(42)}
    testStr = '''
    if 1 == 1
        if 1 < 2
            out = 0
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


    env = tests[-1].env
