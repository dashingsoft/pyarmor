from . import effects
from .filters import vocoder
from . import formats

print('vocoder password inside is: %s' % vocoder.password)
print('effects.__all__ inside is: %s' % ','.join(effects.__all__))
print('all formsts inside are: %s' % ','.join(formats.namelist))
