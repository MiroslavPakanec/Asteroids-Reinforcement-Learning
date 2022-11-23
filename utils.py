import math

def map_value_to_interval(value, origin_min, origin_max, target_min, target_max):
    leftSpan = origin_max - origin_min
    rightSpan = target_max - target_min
    valueScaled = float(value - origin_min) / float(leftSpan)
    return target_min + (valueScaled * rightSpan)

def radians(deg):
    return deg * math.pi / 180