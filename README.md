# mfl-charts
Display charts for MFL leagues

## Installation
Create a `virtualenv` (Python 3)
```
pip install -r requirements.txt
python fiver/manage.py migrate
python fiver/manage.py shell_plus
```
```Python
from apps.stats.populate import *
populate_franchises(LEAGUE_ID, CURRENT_YEAR)
populate_results(LEAGUE_ID, LAST_YEAR)
populate_adp()
```
