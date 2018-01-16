import geom

import csv
import os

__location__=os.path.dirname(os.path.realpath(__file__))

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
            if "ID" in tags and tags["ID"]!="":
                newtags["gnis:feature_id"]=tags["ID"]
                if "wikidata" in tags:
                    newtags["wikidata"]=tags["wikidata"]
                if "wikipedia" in tags:
                    newtags["wikipedia"]=tags["wikipedia"]
        if t=="City":
            newtags["admin_level"]="8"
            newtags["boundary"]="administrative"
    return newtags

def splitWay(way, corners, features_map):
    idxs=sorted([way.points.index(c) for c in corners])
    ends=[0]+idxs+[len(way.points)-1]
    new_points=list()
    for start,end in zip([0]+idxs,idxs+[len(way.points)]):#zip(idxs,idxs[1:]+idxs[:1]):
        if start==end:
            continue
        else:
            new_points.append(way.points[start:(end+1)])
        # glue tails of closed ways back together.
        #~ if way.points[0]==way.points[-1]:
            #~ t=new_points.pop()
            #~ new_points[0]=t[:-1]+new_points[0]
    new_ways = [way, ] + [geom.Way() for i in range(len(new_points) - 1)]

    if way in features_map:
        way_tags = features_map[way].tags

        for new_way in new_ways:
            if new_way != way:
                feat = geom.Feature()
                feat.geometry = new_way
                feat.tags = way_tags
                new_way.addparent(feat)

    for new_way, points in zip(new_ways, new_points):
        new_way.points = points
        if new_way.id != way.id:
            for point in points:
                point.removeparent(way, shoulddestroy=False)
                point.addparent(new_way)
    wls=[len(w.points) for w in new_ways]
    print(len(new_ways),sum(wls),wls)
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

def similar(way1, way2):
    if len(way1.points)!=len(way2.points):
        return False
    w1=[w.id for w in way1.points]
    w2=[w.id for w in way2.points]
    if w1[0] not in w2:
        return False
    if set(w1) != set(w2):
        return False
    # closed way
    if w1[0]==w1[-1]:
        idx1=w1.index(min(w1))
        w1=w1[idx1:-1]+w1[:idx1]
        if w2[0]==w2[-1]:
            idx2=w2.index(min(w2))
            w2=w2[idx2:-1]+w2[:idx2]
        # second way is not closed
        else:
            return False
        if w1==w2:
            return True
        if w1==w2[:1]+w2[1:][::-1]:
            return True
    else:
        if w1==w2:
            return True
        if w1==w2[::-1]:
            return True
    return False

def preOutputTransform(geometries, features):
    if geometries is None and features is None:
        return
    lint(geometries,"At entry")
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
            outers=[m[0] for m in rel.members if m[1]=="outer"]
            relfeat.tags=featuresmap[outers[0]].tags
            for member,role in rel.members:
                if role=="outer" and member in featuresmap:
                    member.removeparent(featuresmap[member])
        else:
            pass
            #~ print("Relation {} has tags.".format(rel.id),relfeat.tags)
    # create relations for ways that are features.
    ways = [g for g in geometries if type(g) == geom.Way]
    for way in ways:
        feature = False
        outers = []
        for parent in way.parents:
            if type(parent) == geom.Feature:
                feature = parent
            #~ if type(parent) == geom.Relation:
                #~ for member,role in parent.members:
                    #~ if role == "outer" and member == way:
                        #~ outers.append(parent)
        if feature:
            newrel = geom.Relation()
            way.addparent(newrel)
            newrel.members.append((way,"outer"))
            feature.replacejwithi(newrel, way)
    print("Splitting relations")
    lint(geometries,"Before split")
    featuresmap = {feature.geometry : feature for feature in features}
    corners = findSharedVertices(geometries)
    ways = [g for g in geometries if type(g) == geom.Way]
    for way in ways:
        is_way_in_relation = len([p for p in way.parents if type(p) == geom.Relation]) > 0
        thesecorners = set(corners).intersection(way.points)
        if len(thesecorners) > 1:
            way_parts = splitWay(way, thesecorners, featuresmap)
            if not is_way_in_relation:
                rel = mergeIntoNewRelation(way_parts)
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
    lint(geometries,"After split")
    print("Merging relations")
    ways = sorted([g for g in geometries if type(g) == geom.Way], key=lambda g: len(g.points))
    # combine duplicate ways.
    removed=list()
    worklist=list(ways)
    for way in ways:
        # skip ways that are already gone
        if way in removed:
            continue
        worklist.remove(way)
        for otherway in worklist:
            if len(otherway.points) > len(way.points):
                break
            if otherway.id!=way.id and similar(way,otherway):
                for parent in list(otherway.parents):
                    if type(parent) == geom.Relation:
                        parent.replacejwithi(way, otherway)
                removed.append(otherway)
    ways=[g for g in geometries if type(g)  == geom.Way]
    featuresmap = {feature.geometry : feature for feature in features}
    for way in ways:
        if way not in featuresmap:
            feat = geom.Feature()
            feat.geometry = way
            feat.tags.update({"admin_level":"7", 
                "boundary":"administrative"})
    lint(geometries,"After combine.")
    for feat in features:
        if type(feat.geometry) == geom.Relation:
            feat.tags["type"]="boundary"


def lint(geometries, message=""):
    ways=[g for g in geometries if type(g) == geom.Way]
    rels=[g for g in geometries if type(g) == geom.Relation]
    results=list()
    # check for geometries with no parents.
    noparents=list()
    results.append(noparents)
    for geo in geometries:
        if len(geo.parents)==0:
            noparents.append(geo)
    # check for duplicate nodes in ways
    dupenodes=list()
    results.append(dupenodes)
    onenodeways=list()
    results.append(onenodeways)
    count=0
    for way in ways:
        for i in range(1,len(way.points)):
            if way.points[i-1]==way.points[i]:
                dupenodes.append(way, i)
                count+=1
        if len(way.points)==1:
            onenodeways.append(way)
            count+=1
    if message and any(results):
        print(message)
    if noparents:
        print("{} geometries with no parents.".format(len(noparents)))
        for p in noparents:
            print(p)
    if dupenodes:
        print("{} duplicate nodes in ways.".format(len(dupenodes)))
    if onenodeways:
        print("{} one node ways.".format(len(onenodeways)))
    