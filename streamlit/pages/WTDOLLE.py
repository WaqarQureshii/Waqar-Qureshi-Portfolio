import pandas as pd
from datetime import datetime

import sys
sys.path.append("..")

from functions.generate_db import generate_vix

vix = generate_vix('2008-01-01')
print(vix)
