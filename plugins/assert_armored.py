def assert_armored(*names):
    from pytransform import _pytransform, PYFUNCTYPE, py_object
    prototype = PYFUNCTYPE(py_object, py_object)
    dlfunc = prototype(('assert_armored', _pytransform))

    def wrapper(func):
        def _execute(*args, **kwargs):

            # Call check point provide by PyArmor
            dlfunc(names)

            # Add your private check code
            # for s in names:
            #     if s.__name__ == 'connect':
            #         if s.__code__.co_code[10:12] != b'\x90\xA2':
            #             raise RuntimeError('Access violate')

            return func(*args, **kwargs)
        return _execute
    return wrapper
