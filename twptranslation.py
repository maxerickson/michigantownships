import csv
import os

__location__=os.path.dirname(os.path.realpath(__file__))


# Special case townships that fail spacial join. The names of the missed
# matchs are unique so no need for further special handling.
townships={
"Caseville":"1626041",
"Eagle Harbor":"1626201",
"Fairhaven":"1626266",
"Glen Arbor":"1626359",
"Gore":"1626365",
"Houghton":"1626493",
"Lake":"1626573",
"Leelanau":"1626601",
"Leland":"1626603",
"Pointe Aux Barques":"1626921",
"Port Austin":"1626928",
"Rubicon":"1627014",
"Sims":"1627084",
"St James":"1627029",
"Suttons Bay":"1627143",
}

townshipmap=dict()
with open(os.path.join(__location__,"mitownships.csv")) as data:
    reader=csv.DictReader(data, delimiter="\t")
    for row in reader:
        townshipmap[row["ID"]]=row

def filterTags(tags):
    if tags is None:
        return
    newtags = {}
    # append " Township"? could also use LABEL
    if "NAME" in tags:
        newtags["name"]=tags["NAME"]
    if "TYPE" in tags:
        t=tags["TYPE"]
        if t=="Township":
            newtags["admin_level"]="7"
            newtags["boundary"]="administrative"
            newtags["border_type"]="township"
            # add gnis and wikidata tags.
            gid=source=None
            if "ID" in tags and tags["ID"]!="":
                gid=tags["ID"]
                source=tags
            elif tags["NAME"] in townships:
                gid=townships[tags["NAME"]]
                source=townshipmap[gid]
            if gid is not None:
                newtags["gnis:feature_id"]=gid
            if source is not None:
                if "wikidata" in source:
                    newtags["wikidata"]=source["wikidata"]
                if "wikipedia" in source:
                    newtags["wikipedia"]=source["wikipedia"]
        if t=="City":
            newtags["admin_level"]="8"
            newtags["boundary"]="administrative"
    return newtags