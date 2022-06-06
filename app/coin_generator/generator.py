'''
    coin_generator
'''
import ctypes


def generate_coin(lib, arg):
    '''
        generate
    '''

    length = len(arg)

    argv_type = (ctypes.c_char_p * length)
    argv_select = argv_type()

    for i, val in enumerate(arg):
        argv_select[i] = val.encode('utf-8')

    lib.main.argtypes = [ctypes.c_int, argv_type]
    lib.main(length, argv_select)
