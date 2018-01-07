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
        if t=="City":
            newtags["admin_level"]="8"
            newtags["boundary"]="administrative"            
    return newtags