Project tracking adding data from http://gis-michigan.opendata.arcgis.com/datasets/minor-civil-divisions-cities-amp-townships-v17a
to OpenStreetMap.

After installing GDAL and retrieving ogr2osm, run this command to generate osm 
data:

    ./ogr2osm/ogr2osm.py -t twptranslation.py  -o twp.osm /share/gis/micivil/
