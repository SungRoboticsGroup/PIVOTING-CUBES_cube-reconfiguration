# vector operations:
# - elementwise addition
# - elementwise subtraction
# - multiplication by a scalar
# - circular shift

def add_t(a, b):
    '''
    a + b componentwise
    '''
    assert type(a) is tuple
    assert type(b) is tuple
    return tuple(a_i + b_i for (a_i, b_i) in zip(a,b))

def sub_t(a, b):
    '''
    a - b componentwise
    '''
    assert type(a) is tuple
    assert type(b) is tuple
    return tuple(a_i - b_i for (a_i, b_i) in zip(a,b))

def sca_t(a, c):
    '''
    c*a
    '''
    assert type(a) is tuple
    return tuple(c*a_i for a_i in a)

def circshift(a, c):
    assert type(a) is tuple
    return tuple(a[(i+c)%len(a)] for i in range(len(a)))
