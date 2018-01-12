#! /bin/bash
ogr2ogr -sql "select t.geometry, t.NAME, t.TYPE,
            g.ID, g.FeatureName, g.County, g.wikidata, g.wikipedia
            from civil t left join micivil g 
            on g.FeatureName LIKE '%Township%' and ST_CONTAINS(t.geometry, g.geometry)
            or t.LABEL LIKE g.FeatureName" -dialect SQLITE test.shp mitownships.vrt
