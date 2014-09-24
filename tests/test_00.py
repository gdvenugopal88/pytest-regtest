def test0(regtest):
    print >> regtest, "this is the expected output "

def test1(regtest):
    print >> regtest, "number one !!"
    assert False

def test2():
    assert True

def test3():
    assert False
