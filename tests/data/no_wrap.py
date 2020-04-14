# pylint: disable=too-many-locals
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

    check_call(_LIB.MXSymbolGetAtomicSymbolInfo(
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
    doc_str = _build_doc(op_name,
                         py_str(desc.value),
                         arg_names,
                         arg_types,
                         [py_str(arg_descs[i]) for i in range(narg)],
                         key_var_num_args,
                         ret_type)

    dtype_name = None
    arr_name = None
    ndsignature = []
    signature = []
    ndarg_names = []
    kwarg_names = []
    for i in range(narg):
        name, atype = arg_names[i], arg_types[i]
        if name == 'dtype':
            dtype_name = name
            signature.append('%s=_Null'%name)
        elif atype.startswith('NDArray') or atype.startswith('Symbol'):
            assert not arr_name, \
                "Op can only have one argument with variable " \
                "size and it must be the last argument."
            if atype.endswith('[]'):
                ndsignature.append('*%s'%name)
                arr_name = name
            else:
                ndsignature.append('%s=None'%name)
                ndarg_names.append(name)
        else:
            signature.append('%s=_Null'%name)
            kwarg_names.append(name)
    signature.append('out=None')
    signature.append('name=None')
    signature.append('**kwargs')
    signature = ndsignature + signature

    code = []
    is_np_op = _is_np_op(op_name)
    doc_str_idx = 1
    if is_np_op:
        doc_str_idx = 2
    if arr_name:
        code.append("""
def %s(*%s, **kwargs):"""%(func_name, arr_name))
        if not signature_only:
            code.append("""
    ndargs = []
    for i in {}:
        assert isinstance(i, NDArrayBase), \\
            "Positional arguments must have NDArray type, " \\
            "but got %s"%str(i)
        ndargs.append(i)""".format(arr_name))
            if dtype_name is not None:
                code.append("""
    if '%s' in kwargs:
        kwargs['%s'] = _np.dtype(kwargs['%s']).name"""%(
            dtype_name, dtype_name, dtype_name))
            code.append("""
    _ = kwargs.pop('name', None)
    out = kwargs.pop('out', None)
    keys = list(kwargs.keys())
    vals = list(kwargs.values())""")
    else:
        code.append("""
def %s(%s):"""%(func_name, ', '.join(signature)))
        if not signature_only:
            code.append("""
    ndargs = []
    keys = list(kwargs.keys())
    vals = list(kwargs.values())""")
            # NDArray args
            for name in ndarg_names: # pylint: disable=redefined-argument-from-local
                code.append("""
    if {name} is not None:
        assert isinstance({name}, NDArrayBase), \\
            "Argument {name} must have NDArray type, but got %s"%str({name})
        ndargs.append({name})""".format(name=name))
            # kwargs
            for name in kwarg_names: # pylint: disable=redefined-argument-from-local
                code.append("""
    if %s is not _Null:
        keys.append('%s')
        vals.append(%s)"""%(name, name, name))
            # dtype
            if dtype_name is not None:
                if is_np_op:
                    code.append("""
    if %s is not _Null and %s is not None:
        keys.append('%s')
        vals.append(_np.dtype(%s).name)"""%(dtype_name, dtype_name, dtype_name, dtype_name))
                else:
                    code.append("""
    if %s is not _Null:
        keys.append('%s')
        vals.append(_np.dtype(%s).name)"""%(dtype_name, dtype_name, dtype_name))

    verify_ndarrays_fn =\
        _verify_all_np_ndarrays.__name__ if is_np_op else _verify_all_legacy_ndarrays.__name__
    if not signature_only:
        code.append("""
    {verify_fn}("{op_name}", "{func_name}", ndargs, out)
        """.format(verify_fn=verify_ndarrays_fn, op_name=op_name, func_name=func_name))
        code.append("""
    return _imperative_invoke(%d, ndargs, keys, vals, out, %s)"""%(
        handle.value, str(is_np_op)))
    else:
        code.append("""
    return (0,)""")

    doc_str_lines = _os.linesep+''.join(['    '+s if s.strip() else s
                                         for s in 'r"""{doc_str}"""'.format(doc_str=doc_str)
                                         .splitlines(True)])
    code.insert(doc_str_idx, doc_str_lines)
    return ''.join(code), doc_str



