import talib
import numpy 
import os 

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'relative/path/to/file/you/want')
close = numpy.random.random(100)
output = talib.SMA(close)
print(output)