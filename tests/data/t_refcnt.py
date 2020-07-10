import sys
import threading
import weakref


class RunSelfFunction(object):

    def __init__(self, should_raise):
        # The links in this refcycle from Thread back to self
        # should be cleaned up when the thread completes.
        self.should_raise = should_raise
        self.thread = threading.Thread(target=self._run,
                                       args=(self,),
                                       kwargs={'yet_another': self})
        self.thread.start()

    def _run(self, other_ref, yet_another):
        if self.should_raise:
            raise SystemExit


def test_target_refcnt():
    cyclic_object = RunSelfFunction(should_raise=False)
    weak_cyclic_object = weakref.ref(cyclic_object)
    cyclic_object.thread.join()
    del cyclic_object
    print('No raise target shoule be None: %s' % weak_cyclic_object())
    print('%d references still around' %
          sys.getrefcount(weak_cyclic_object()))

    raising_cyclic_object = RunSelfFunction(should_raise=True)
    weak_raising_cyclic_object = weakref.ref(raising_cyclic_object)
    raising_cyclic_object.thread.join()
    del raising_cyclic_object
    print('Raise target shoule be None: %s' % weak_raising_cyclic_object())
    print('%d references still around' %
          sys.getrefcount(weak_raising_cyclic_object()))


test_target_refcnt()
