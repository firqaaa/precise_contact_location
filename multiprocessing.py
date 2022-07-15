import sys
import time
import traceback
import numpy as np
import multiprocessing
from functools import partial
from tqdm.notebook import tqdm
from joblib import parallel_backend
from joblib import Parallel, delayed
from joblib import wrap_non_picklable_objects
from joblib.externals.loky import set_loky_pickler

lines = []
with open("../input/2300k-loc/2300k_loc.txt", "r", encoding="utf-8") as f:
  lines = f.readlines()

loc = []
for line in lines:
  loc.append(line.strip())

# loc = np.unique(loc)
get_location_ = partial(get_locations)

with parallel_backend('multiprocessing'):
    t_start = time.time()
    result = Parallel(n_jobs=multiprocessing.cpu_count())(
        delayed(get_location_)(j) for i, j in tqdm(enumerate(loc[:100000]), total=len(loc[:100000])))
    print("With multiprocessing backend and pickle serialization: {:.3f}s"
          .format(time.time() - t_start))
