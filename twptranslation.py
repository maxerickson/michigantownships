
# Special case townships that fail spacial join. The names of the missed
# matchs are unique so no need for further special handling.
townships={
"Caseville":("Township of Caseville","1626041"),
"Eagle Harbor":("Township of Eagle Harbor","1626201"),
"Fairhaven":("Township of Fairhaven","1626266"),
"Glen Arbor":("Township of Glen Arbor","1626359"),
"Gore":("Township of Gore","1626365"),
"Houghton":("Township of Houghton","1626493"),
"Lake":("Township of Lake","1626573"),
"Leelanau":("Township of Leelanau","1626601"),
"Leland":("Township of Leland","1626603"),
"Pointe Aux Barques":("Township of Pointe Aux Barques"),
"Port Austin":("Township of Port Austin","1626928"),
"Rubicon":("Township of Rubicon","1627014"),
"Sims":("Township of Sims","1627084"),
"St James":("Township of Saint James","1627029"),
"Suttons Bay":("Township of Suttons Bay","1627143"),
}

def filterTags(tags):
    if tags is None:
        return
    newtags = {}
    # append " Township"? could also use LABEL
    if "NAME" in tags:
        newtags["name"]=tags["NAME"]
    if "ID" in tags:
        newtags["gnis:feature_id"]=tags["ID"]
    elif tags["NAME"] in townships:
        newtags["gnis:feature_id"]=townships[tags["NAME"]][1]
    if "TYPE" in tags:
        t=tags["TYPE"]
        if t=="Township":
            newtags["admin_level"]="7"
            newtags["boundary"]="administrative"
            newtags["border_type"]="township"
            gnisname=None
            if "FeatureNam" in tags:
                gnisname=tags["FeatureNam"]
            elif tags["NAME"] in townships:
                gnisname=townships[tags["NAME"]]
            if gnisname is not None:
                pass
        if t=="City":
            newtags["admin_level"]="8"
            newtags["boundary"]="administrative"
    return newtags