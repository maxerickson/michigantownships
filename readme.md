Project tracking adding data from http://gis-michigan.opendata.arcgis.com/datasets/minor-civil-divisions-cities-amp-townships-v17a
to OpenStreetMap.

Data prep requires GDAL and ogr2osm and curl.

Use mitwp.sparq to fetch wikidata ids:

    curl -G https://query.wikidata.org/sparql? -o wikidata.csv -H "Accept: text/csv" --data-urlencode query="$(< mitwp.sparql)"

Obtain items in Michigan of class "civil" from GNIS and preprocess to adjust
format and merge in wikidata/wikipedia info:

    python formatgnis.py mitownshipsgnis.csv mitownships.csv

Join the gnis and wiki data with the shapefile:

    ./joindata.sh

Generate osm data:

    ./ogr2osm/ogr2osm.py -t twptranslation.py  -o twp.osm test.shp

Manually clean up incorrect roles.

Split data into files by county:

    python makedata.py manually_cleaned.osm output


Create a sample:

    ogr2ogr -where "NAME in ('Houghton','Eagle Harbor') and TYPE='Township'" sample.shp test.shp
