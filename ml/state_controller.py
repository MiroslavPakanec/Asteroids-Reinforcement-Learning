import numpy as np

def process_state(arr):
    a = np.array(arr)
    f_c_to_gs = lambda x: 0.3 * (np.floor(x / 65536)) + 0.59 * (np.floor(x / 256) % 256) + 0.11 * (x % 256)
    gs = f_c_to_gs(a)
    return gs
    

