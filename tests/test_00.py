from __future__ import print_function


def test0(regtest):
    print("test0")
    print("this is the expected output\t", file=regtest)


def test1(regtest):
    print("test1")
    print("number one !!", file=regtest)
    assert False


def test2():
    assert True


def test3():
    assert False


def test4(regtest_redirect):
    with regtest_redirect():
        print("hi")


def test_with_object_id(regtest):
    print (test_with_object_id, file=regtest)
