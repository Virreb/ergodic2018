import numpy as np
from sys import getsizeof

test = np.random.randint(0,10, size=(10000, 10000, 5))

print(getsizeof(test)/1000000)
