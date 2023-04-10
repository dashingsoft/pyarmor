import logging

__VERSION__ = '8.1'

logger = logging.getLogger('cli')


def resoptions(meth):

    def process(self, res, *args, **kwargs):
        self._options = self.ctx.get_res_options(res.fullname, self._Catalog)
        return meth(self, res, *args, **kwargs)

    return process


class Component(object):

    trace_loggers = {
        'StrProtector': 'trace.mix.str',
        'CallProtector': 'trace.assert.call',
        'ImportProtector': 'trace.assert.import',
        'CodeProtector': 'trace.co',
        'CoPatcher': 'trace.co',
        'BccPatcher': 'trace.bcc',
    }

    def __init__(self, ctx):
        self.ctx = ctx
        self._options = {}

        clsname = self.__class__.__name__
        self.logger = logging.getLogger(self.trace_loggers[clsname])

    def __getattr__(self, opt):
        if opt.startswith('o_'):
            return self._options.get(opt[2:], '')
        elif opt.startswith('oi_'):
            return int(self._options.get(opt[3:]))
        elif opt.startswith('ob_'):
            v = self._options.get(opt[3:], '')
            if isinstance(v, str):
                return v.lower() in ('1', 'true', 'on', 'yes')
            return v
        return AttributeError(opt)

    def trace(self, res, node, value):
        lineno = getattr(node, 'lineno', -1)
        self.logger.info('%s:%s:%s', res.fullname, lineno, value)
