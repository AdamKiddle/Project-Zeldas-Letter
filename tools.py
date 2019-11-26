import numpy as np
from random import randint
from random import seed
seed()

def get_hex(number_value,padding=6):
    """
    Takes an integer value and returns it as a hex string (0x...) of number_value.
    ============INPUTS================
    number_value:    int
            Input value to turn into hex.
    padding:         int
            minimum number of digits after 0x (default 6)
    """
    # Deal with numpy arrays:
    if type(number_value) == np.ndarray:
        np_hex = np.vectorize(('0x{:0'+str(padding)+'X}').format)
        return np_hex(number_value.astype(int))
    
    # Deal with single scalar numbers:
    else:
        return (('0x{:0'+str(padding)+'X}')).format(int(number_value))
    
def is_hex(s):
    """
    Takes an input string and checks if it's hex.
    """
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

def process_line(line):
    """
    Takes an input string and removes non-alphanumeric characters other than "," "_" and "."
    Also deals with comments (all characters after # are ignored)
    
    Outputs:
        out:       the processed string
        comma_idx: list of positions in the string where commas exist.
    """
    out = ""
    comma_idx = []
    for i in range(len(line)):
        if line[i] == "#":
            # Ignore anything after hash
            break
        elif line[i] == ',':
            out += line[i]
            comma_idx.append(i)
        elif str.isalnum(line[i]) or line[i] == "_" or line[i] == ".":
            out += line[i]
    return out, comma_idx

def pick_random(n_ind):
    """
    returns a list of n random but different indices from 0  up to n_ind
    """
    n_picks = randint(0,n_ind)
    in_pool = np.arange(n_ind)
    out_pool = []
    
    for i in range(n_picks):
            pick = randint(0,n_ind-1-i)
            out_pool.append(in_pool[pick])
            in_pool = np.delete(in_pool,pick)
    return out_pool