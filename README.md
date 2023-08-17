# Polygon Search Examples  

## Contents
1.  [Summary](#summary)
2.  [Features](#features)
3.  [Prerequisites](#prerequisites)
4.  [Installation](#installation)
5.  [Usage](#usage)

## Summary <a name="summary"></a>
This is a Python demo of Polygon Search capabilities available with 7.2 Redis Stack.  This builds 4 random polygons and points via the Shapely module.  The 4 polygons are arranged to be layered in containment with 4 points within them.  The polygons and points are stored in Redis as JSON objects.  Redis Search is then leveraged to show the WITHIN and CONTAINS query types.


## Features <a name="features"></a>
- Creates 4 random polygons + points and plots them on a graphical display
- Stores the Polygons and Points in Redis as JSON objects
- Performs Redis geo searches leveraging the WITHIN and CONTAINS queries  

## Prerequisites <a name="prerequisites"></a>
- Docker Compose
- Python

## Installation <a name="installation"></a>
1. Clone this repo.

2.  Install Python requirements
```bash
pip install -r requirements.txt
```

3.  Start Redis Stack
```bash
docker compose up -d
```

## Usage <a name="usage"></a>
### Execution
```bash
python3 poly.py
```

### Plot
![plot](./assets/figure1.png)

### Results
```text
*** Polygons within the Red Polygon ***
Green Polygon
Blue Polygon
Cyan Polygon

*** Polygons within the Green Polygon ***
Blue Polygon
Cyan Polygon

*** Polygons within the Blue Polygon ***
Cyan Polygon

*** Polygons within the Cyan Polygon ***
None

*** Points within the Red Polygon ***
Purple Point
Brown Point
Orange Point
Olive Point

*** Points within the Green Polygon ***
Purple Point
Brown Point
Orange Point
Olive Point

*** Points within the Blue Polygon ***
Purple Point
Brown Point

*** Points within the Cyan Polygon ***
Purple Point
Brown Point

*** Polygons containing the Red Polygon ***
None

*** Polygons containing the Green Polygon ***
Red Polygon

*** Polygons containing the Blue Polygon ***
Red Polygon
Green Polygon

*** Polygons containing the Cyan Polygon ***
Red Polygon
Green Polygon
Blue Polygon

*** Polygons containing the Purple Point ***
Red Polygon
Green Polygon
Blue Polygon
Cyan Polygon

*** Polygons containing the Brown Point ***
Red Polygon
Green Polygon
Blue Polygon
Cyan Polygon

*** Polygons containing the Orange Point ***
Red Polygon
Green Polygon

*** Polygons containing the Olive Point ***
Red Polygon
Green Polygon
```