import geom

import csv
import os

__location__=os.path.dirname(os.path.realpath(__file__))


# Special case townships that fail spacial join. The names of the missed
# matchs are unique so no need for further special handling.
townships={
#~ "Caseville":"1626041",
#~ "Eagle Harbor":"1626201",
#~ "Fairhaven":"1626266",
#~ "Glen Arbor":"1626359",
#~ "Gore":"1626365",
#~ "Houghton":"1626493",
#~ "Lake":"1626573",
#~ "Leelanau":"1626601",
#~ "Leland":"1626603",
#~ "Pointe Aux Barques":"1626921",
#~ "Port Austin":"1626928",
#~ "Rubicon":"1627014",
#~ "Sims":"1627084",
#~ "St James":"1627029",
#~ "Suttons Bay":"1627143",
}

townshipmap=dict()
with open(os.path.join(__location__,"mitownships.csv")) as data:
    reader=csv.DictReader(data)
    for row in reader:
        townshipmap[row["ID"]]=row

def filterTags(tags):
    if tags is None:
        return
    newtags = {}
    # append " Township"? could also use LABEL
    for t in ["name","county"]:
        if t in tags:
            newtags[t]=tags[t]
    if "border_typ" in tags:
        t=tags["border_typ"]
        newtags["border_type"]=t.lower()
        if t=="Township":
            newtags["admin_level"]="7"
            newtags["boundary"]="administrative"
            # add gnis and wikidata tags.
            gid=source=None
            if "ID" in tags and tags["ID"]!="":
                gid=tags["ID"]
                source=tags
            elif tags["name"] in townships:
                gid=townships[tags["name"]]
                source=townshipmap[gid]
                newtags["county"]=source["County"]
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

def splitWay(way, corners, features_map):
    idxs=sorted([way.points.index(c) for c in corners])
    new_points=list()
    for a,b in zip(idxs,idxs[1:]+idxs[:1]):
        if a==b:
            continue
        elif a < b:
            new_points.append(way.points[a:b+1])
        else:
            # glue "tails" of circular ways together
            if way.points[-1]==way.points[0]:
                new_points.append(way.points[a:]+way.points[1:b+1])
            else:
                new_points.append(way.points[a:])
                new_points.append(way.points[:b+1])
    new_ways = [way, ] + [geom.Way() for i in range(len(new_points) - 1)]

    if way in features_map:
        way_tags = features_map[way].tags

        for new_way in new_ways:
            if new_way != way:
                feat = geom.Feature()
                feat.geometry = new_way
                feat.tags = way_tags

    for new_way, points in zip(new_ways, new_points):
        new_way.points = points
        if new_way.id != way.id:
            for point in points:
                point.removeparent(way, shoulddestroy=False)
                point.addparent(new_way)

    return new_ways

def mergeIntoNewRelation(way_parts):
    new_relation = geom.Relation()
    feat = geom.Feature()
    feat.geometry = new_relation
    new_relation.members = [(way, "outer") for way in way_parts]
    for way in way_parts:
        way.addparent(new_relation)
    return feat

def splitWayInRelation(rel, way_parts):
    way_roles = [m[1] for m in rel.members if m[0] == way_parts[0]]
    way_role = "" if len(way_roles) == 0 else way_roles[0]
    for way in way_parts[1:]:
        way.addparent(rel)
        rel.members.append((way, way_role))

def findSharedVertices(geometries):
    points = [g for g in geometries if type(g) == geom.Point and len(g.parents) > 1]
    vertices=list()
    for p in points:
        neighbors=set()
        for way in p.parents:
            idx=way.points.index(p)
            if idx > -1:
                for step in [-1,1]:
                    pt=way.points[(idx+step)%len(way.points)].id
                    # Take an extra step at the ends of circular ways.
                    if pt==p.id:
                        pt=way.points[(idx+2*step)%len(way.points)].id
                    neighbors.add(pt)
        if len(neighbors) > 2:
            vertices.append(p)
    return vertices

def preOutputTransform(geometries, features):
    if geometries is None and features is None:
        return
    featuresmap = {feature.geometry : feature for feature in features}
    print("Moving tags to relations")
    # move tags, remove member ways as Features.
    rels=[g for g in geometries if type(g) == geom.Relation]
    for rel in rels:
        # splitWayInRelation does not add the relation as a parent.
        for member,role in rel.members:
            if rel not in member.parents:
                member.addparent(rel)
        relfeat=featuresmap[rel]
        if relfeat.tags=={}:
            relfeat.tags=featuresmap[rel.members[0][0]].tags
            for member,role in rel.members:
                if member in featuresmap:
                    member.removeparent(featuresmap[member])
        else:
            pass
            #~ print("Relation {} has tags.".format(rel.id),relfeat.tags)
    print("Splitting relations")
    lint(geometries,"Before split")
    corners = findSharedVertices(geometries)
    ways = [g for g in geometries if type(g) == geom.Way]
    for way in ways:
        is_way_in_relation = len([p for p in way.parents if type(p) == geom.Relation]) > 0
        thesecorners = set(corners).intersection(way.points)
        if len(thesecorners) > 1:
            way_parts = splitWay(way, thesecorners, featuresmap)
            if not is_way_in_relation:
                rel=mergeIntoNewRelation(way_parts)
                featuresmap = {feature.geometry : feature for feature in features}
                if way in featuresmap:
                    rel.tags.update(featuresmap[way].tags)
                for wg,role in rel.geometry.members:
                    if wg in featuresmap:
                        wg.removeparent(featuresmap[wg])
            else:
                for parent in way.parents:
                    if type(parent)==geom.Relation:
                        splitWayInRelation(parent, way_parts)
    print("Merging relations")
    lint(geometries,"After split")
    ways = [g for g in geometries if type(g) == geom.Way]
    # combine duplicate ways.
    worklist=ways
    def similar(way1, way2):
        if way1.points==way2.points:
            return True
        if list(reversed(way1.points))==way2.points:
            return True
        return False
    for way in worklist:
        # skip ways that are already gone
        if way not in ways:
            continue
        for otherway in ways:
            if otherway.id!=way.id and similar(way,otherway):
                for parent in list(otherway.parents):
                    if type(parent)==geom.Relation:
                        parent.replacejwithi(way, otherway)
                ways.remove(otherway)
    for way in ways:
        feat = geom.Feature()
        feat.geometry = way
        feat.tags = {"admin_level":"7", 
                            "boundary":"administrative"}
    for feat in features:
        if "type" in feat.tags:
            feat.tags["type"]="boundary"


def lint(geometries, message=""):
    ways=[g for g in geometries if type(g) == geom.Way]
    rels=[g for g in geometries if type(g) == geom.Relation]
    # check for duplicate nodes in ways
    dupenodes=list()
    onenodeways=list()
    count=0
    for way in ways:
        for i in range(1,len(way.points)):
            if way.points[i-1]==way.points[i]:
                dupenodes.append(way.id, i)
                count+=1
        if len(way.points)==1:
            onenodeways.append(way.id)
            count+=1
    if count and message:
        print(message)
    if dupenodes:
        print("{} duplicate nodes in ways.".format(len(dupenodes)))
    if onenodeways:
        print("{} one node ways.".format(len(onenodeways)))
    