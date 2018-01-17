#! /bin/bash
ogr2ogr -sql "select t.geometry, t.NAME as name, t.TYPE as border_type,
            g.ID, g.FeatureName, g.County as county, g.wikidata, g.wikipedia
            from civil t left join micivil g on (g.FeatureName LIKE '%Township%'
		   and ST_CONTAINS(t.geometry, g.geometry))
            or t.LABEL LIKE g.FeatureName"  -dialect SQLITE test.shp mitownships.vrt