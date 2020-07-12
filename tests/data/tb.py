import sys
import traceback


def test_clear():
    def outer():
        middle()
    def middle():
        inner()
    def inner():
        i = 1
        1/0

    try:
        outer()
    except:
        type_, value, tb = sys.exc_info()

    # Initial assertion: there's one local in the inner frame.
    p = tb
    while p is not None:
        print('frame is %s' % p.tb_frame.f_code.co_name)
        p = p.tb_next
    inner_frame = tb.tb_next.tb_next.tb_next.tb_frame
    print('inner_frame.flocals is %s' % inner_frame.f_locals)

    # Clear traceback frames
    traceback.clear_frames(tb)

    # Local variable dict should now be empty.
    print('After clear, inner_frame.flocals is %s' % inner_frame.f_locals)


test_clear()
