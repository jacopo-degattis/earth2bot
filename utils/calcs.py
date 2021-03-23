import math
import numpy

def getCordinates(quadkey):
    x=0
    y=0
    z=quadkey % 100

    quadkey = bin(math.trunc(quadkey/100)).replace("0b", "")
    quadkey = list(str(quadkey))

    if (len(quadkey) < z * 2):
        quadkey = numpy.array(z * 2 - len(quadkey)).fill('0').concat(quadkey)

    for i in range(len(quadkey)-1,0,-2):
        digit = int(quadkey[i-1]) * 2 + int(quadkey[i])

        mask = 1 << math.floor(i / 2)
    
        if digit == 1:
            x = x | mask
        elif digit == 2:
            y = y | mask
        elif digit == 3:
            x = x | mask
            y = y | mask

    return y, x, z
  
def get_long(x, z):
    long = (int(x) / math.pow(2, int(z)) * 360) - 180
    return long
    
def get_lat(y, z):
    n = math.pi - 2 * math.pi * y / math.pow(2, z)
    lat = (180/math.pi) * math.atan(0.5 * (math.exp(n) - math.exp(-n)))
    return lat
