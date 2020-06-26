import ctypes

mx_uint = ctypes.c_uint
py_str = lambda x: x


def check_call(ret):
    return ret


def MXSymbolGetAtomicSymbolInfo(*args):
    return len(args)


def _generate_ndarray_function_code(handle, op_name, func_name, signature_only=False):
    """Generate function for ndarray op by handle and function op_name."""
    real_name = ctypes.c_char_p()
    desc = ctypes.c_char_p()
    num_args = mx_uint()
    arg_names = ctypes.POINTER(ctypes.c_char_p)()
    arg_types = ctypes.POINTER(ctypes.c_char_p)()
    arg_descs = ctypes.POINTER(ctypes.c_char_p)()
    key_var_num_args = ctypes.c_char_p()
    ret_type = ctypes.c_char_p()

    check_call(MXSymbolGetAtomicSymbolInfo(
        handle, ctypes.byref(real_name), ctypes.byref(desc),
        ctypes.byref(num_args),
        ctypes.byref(arg_names),
        ctypes.byref(arg_types),
        ctypes.byref(arg_descs),
        ctypes.byref(key_var_num_args),
        ctypes.byref(ret_type)))
    narg = int(num_args.value)
    arg_names = [py_str(arg_names[i]) for i in range(narg)]
    arg_types = [py_str(arg_types[i]) for i in range(narg)]
    key_var_num_args = py_str(key_var_num_args.value)
    ret_type = py_str(ret_type.value) if ret_type.value is not None else ''

    return 'OK'


print('Test no wrap obfuscate mode: %s' %
      _generate_ndarray_function_code('handle', 'op', 'func'))
