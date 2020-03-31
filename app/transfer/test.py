import re
from datetime import datetime as DT

val = '10-10-1000'
print(re.search('([\d]{2,2}-[\d]{2,2}-[\d]{4,4})', val))
