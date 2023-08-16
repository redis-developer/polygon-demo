import matplotlib.pyplot as plt
import random
from typing import List
from shapely import Point, Polygon, MultiPoint
from redis import Connection, from_url
from enum import Enum

REDIS_URL = 'redis://localhost:6379'
MIN_X = 0
MAX_X = 10
MIN_Y = 0
MAX_Y = 10

class QUERY(Enum):
    WITHIN      = 'within'
    CONTAINS    = 'contains'

class COLOR(Enum):
    RED     = 'red'
    GREEN   = 'green'
    BLUE    = 'blue'
    CYAN    = 'cyan'
    PURPLE  = 'purple'
    BROWN   = 'brown'
    ORANGE  = 'orange'
    OLIVE   = 'olive'

class SHAPE(Enum):
    POLYGON = 'Polygon'
    POINT = 'Point'

class PolygonDemo(object):
    def __init__(self):
        self.client: Connection = from_url(REDIS_URL)
        self.client.flushdb()

    def demo(self) -> None:
        """ Public function that creates 4 random polygons and points.  The shapes are aligned in layers such that the 4th is contained by the 3rd,
        the 3rd by the 2nd, etc.  Each shape is stored as a JSON object in Redis with its name and WKT parameters.  Finally, a series
        of searches exercising the Redis WITHIN and CONTAINS queries are executed.  Note at the time of the writing the GEOMETRY and POLYGON
        keywords are not supported in the redis-py lib.  This function is sending raw CLI commands to Redis.

        Returns
        -------
        None
        """
        poly_red: Polygon   = self._get_polygon()
        poly_green: Polygon = self._get_polygon(poly_red) 
        poly_blue: Polygon  = self._get_polygon(poly_green)
        poly_cyan: Polygon  = self._get_polygon(poly_blue)

        point_purple: Point = self._get_point(poly_cyan)
        point_brown: Point  = self._get_point(poly_blue)
        point_orange: Point = self._get_point(poly_green)
        point_olive: Point  = self._get_point(poly_red)

        self.client.execute_command('FT.CREATE', 'idx', 'ON', 'JSON', 'PREFIX', '1', 'key:',
            'SCHEMA', '$.name', 'AS', 'name', 'TEXT', '$.geom', 'AS', 'geom', 'GEOSHAPE', 'FLAT')
        self.client.json().set('key:1', '$', { "name": "Red Polygon", "geom":   poly_red.wkt })
        self.client.json().set('key:2', '$', { "name": "Green Polygon", "geom": poly_green.wkt })
        self.client.json().set('key:3', '$', { "name": "Blue Polygon", "geom":  poly_blue.wkt })
        self.client.json().set('key:4', '$', { "name": "Cyan Polygon", "geom":  poly_cyan.wkt })
        self.client.json().set('key:5', '$', { "name": "Purple Point", "geom":  point_purple.wkt })
        self.client.json().set('key:6', '$', { "name": "Brown Point", "geom":   point_brown.wkt })
        self.client.json().set('key:7', '$', { "name": "Orange Point", "geom":  point_orange.wkt })
        self.client.json().set('key:8', '$', { "name": "Olive Point", "geom":   point_olive.wkt })
        
        print('\n*** Search 1a - Polygons within the Red Polygon ***')
        self._poly_search(QUERY.WITHIN, COLOR.RED, poly_red, SHAPE.POLYGON)
        print('\n*** Search 1b - Points within the Red Polygon ***')
        self._poly_search(QUERY.WITHIN, COLOR.RED, poly_red, SHAPE.POINT)

        print('\n*** Search 2a - Polygons within the Green Polygon ***')
        self._poly_search(QUERY.WITHIN, COLOR.GREEN, poly_green, SHAPE.POLYGON)
        print('\n*** Search 2b - Points within the Green Polygon ***')
        self._poly_search(QUERY.WITHIN, COLOR.GREEN, poly_green, SHAPE.POINT)

        print('\n*** Search 3a - Polygons within the Blue Polygon ***')
        self._poly_search(QUERY.WITHIN, COLOR.BLUE, poly_blue, SHAPE.POLYGON)
        print('\n*** Search 3b - Points within the Blue Polygon ***')
        self._poly_search(QUERY.WITHIN, COLOR.BLUE, poly_blue, SHAPE.POINT)

        print('\n*** Search 4a - Polygons within the Cyan Polygon ***')
        self._poly_search(QUERY.WITHIN, COLOR.CYAN, poly_cyan, SHAPE.POLYGON)
        print('\n*** Search 4b - Points within the Cyan Polygon ***')
        self._poly_search(QUERY.WITHIN, COLOR.CYAN, poly_cyan, SHAPE.POINT)

        print('\n*** Search 5 - Polygons containing the Red Polygon ***')
        self._poly_search(QUERY.CONTAINS, COLOR.RED, poly_red, SHAPE.POLYGON)
        print('\n*** Search 6 - Polygons containing the Green Polygon ***')
        self._poly_search(QUERY.CONTAINS, COLOR.GREEN, poly_green, SHAPE.POLYGON)
        print('\n*** Search 7 - Polygons containing the Blue Polygon ***')
        self._poly_search(QUERY.CONTAINS, COLOR.BLUE, poly_blue, SHAPE.POLYGON)
        print('\n*** Search 8 - Polygons containing the Cyan Polygon ***')
        self._poly_search(QUERY.CONTAINS, COLOR.CYAN, poly_cyan, SHAPE.POLYGON)
        
        plt.plot(*poly_red.exterior.xy, c=COLOR.RED.value)
        plt.plot(*poly_green.exterior.xy, c=COLOR.GREEN.value)
        plt.plot(*poly_blue.exterior.xy, c=COLOR.BLUE.value)
        plt.plot(*poly_cyan.exterior.xy, c=COLOR.CYAN.value)
        
        plt.scatter(point_purple.x, point_purple.y, c=COLOR.PURPLE.value)
        plt.scatter(point_brown.x, point_brown.y, c=COLOR.BROWN.value)
        plt.scatter(point_orange.x, point_orange.y, c=COLOR.ORANGE.value)
        plt.scatter(point_olive.x, point_olive.y, c=COLOR.OLIVE.value)
        plt.show()

    def _poly_search(self, qt: QUERY, color: COLOR, shape: Polygon, filter: SHAPE) -> None:
        """ Private function for POLYGON search in Redis. 
        Parameters
        ----------
        qt - Redis Geometry search type (contains or within)
        color - color attribute of polygon
        shape - Shapely point or polygon object
        filter - query filter on shape types (polygon or point) to be returned

        Returns
        -------
        None
        """
        results: list = self.client.execute_command('FT.SEARCH', 'idx', f'(-@name:{color.value} @name:{filter.value} @geom:[{qt.value} $qshape])', 'PARAMS', '2', 'qshape', shape.wkt, 'RETURN', '1', 'name', 'DIALECT', '3')
        if (results[0] > 0):
            for res in results:
                if isinstance(res, list):
                    print(res[1].decode('utf-8').strip('[]"'))
        else:
            print('None')

    def _get_point(self, box: Polygon = None) -> Point:
        """ Private function to generate a random point, potentially within a bounding box
        Parameters
        ----------
        box - Optional bounding box
  
        Returns
        -------
        Shapely Point object
        """
        point: Point
        if box:
            minx, miny, maxx, maxy = box.bounds
            while True:
                point = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
                if box.contains(point):
                    break
        else:
            point = Point(random.uniform(MIN_X, MAX_X), random.uniform(MIN_Y, MAX_Y))
        return point
    
    def _get_polygon(self, box: Polygon = None) -> Polygon:
        """ Private function to generate a random polygon, potentially within a bounding box
        Parameters
        ----------
        box - Optional bounding box
  
        Returns
        -------
        Shapely Polygon object
        """
        points: List[Point] = []
        for _ in range(random.randint(3,10)):
            points.append(self._get_point(box)) 
        ob: MultiPoint = MultiPoint(points)   
        return Polygon(ob.convex_hull)
  
if __name__ == '__main__':  
    pd: PolygonDemo = PolygonDemo()
    pd.demo()