import numpy
import scipy.misc as misc

sgn = numpy.array([ 1.0-1.0 * (i % 2)*2 for i in range(171)], dtype='float64')
fact = numpy.array([ misc.factorial(i, exact=True) for i in range(171)], dtype='float64')
onedivsqrt4pi = 1.0/numpy.sqrt(4.0*numpy.pi)
rttwo=numpy.sqrt(2.0)
