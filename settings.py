SEARCH_KEY = "AIzaSyCpLlblF5OKZ3d_smVe0hT1jhmAEDf5Knw"
SEARCH_ID = "c33517b13b0914474"
COUNTRY = ""
SEARCH_URL = "https://www.googleapis.com/customsearch/v1?key={key}&cx={cx}&q={query}&start={start}&num=10&gl=" + COUNTRY
RESULT_COUNT = 20

import os
if os.path.exists("private.py"):
    from private import *