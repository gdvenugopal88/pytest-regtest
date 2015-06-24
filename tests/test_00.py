def test0(regtest):
    print "test0"
    print >> regtest, "this is the expected output\t"

def test1(regtest):
    print "test1"
    print >> regtest, "number one !!"
    assert False

def test2():
    assert True

def test3():
    assert False

def test4(regtest_redirect):
    with regtest_redirect():
        print "hi"

def test_with_object_id(regtest):
    print >> regtest, test_with_object_id
