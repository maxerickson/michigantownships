Project tracking adding data from http://gis-michigan.opendata.arcgis.com/datasets/minor-civil-divisions-cities-amp-townships-v17a
to OpenStreetMap.

Data prep requires GDAL and ogr2osm and curl.

Use mitwp.sparq to fetch wikidata ids:

    curl -G https://query.wikidata.org/sparql? -o wikidata.csv -H "Accept: text/csv" --data-urlencode query="$(< mitwp.sparql)"

Obtain township data from gnis and preprocess to format ogr understands.

    python formatgnis.py mitownshipsgnis.csv mitownships.csv

Use mitownships.vrt to do a spatial join adding the gnis id and name to 
the boundaries.

    ogr2ogr -sql "select t.*, g.ID, g.FeatureName, g.wikidata, g.wikipedia from civil t left join mitownships g on ST_CONTAINS(t.geometry, g.geometry)" -dialect SQLITE test.shp mitownships.vrt

(this creates a bunch of warnings; the fields warned about aren't important)

Generate osm data:

    ./ogr2osm/ogr2osm.py -t twptranslation.py  -o twp.osm test.shp

