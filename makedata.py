#! /bin/python
import os
import os.path
import argparse

import xml.etree.ElementTree as ElementTree


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Process GNIS pipe separated file for use with OGR.')
    parser.add_argument('infile',
                        help='Source data')
    parser.add_argument('target',
                        help='Target directory')
    args = parser.parse_args()

    if not os.path.exists(args.target):
        os.mkdir(args.target)
    # build up maps of nodes and ways and per county lists of relations.
    tree=ElementTree.parse(args.infile)
    osm=tree.getroot()
    counties=dict()
    items={
    'node' : dict(),
    'way' : dict(),
    }
    for child in osm:
        if child.tag in {"relation"}:
            try:
                county=child.findall("./tag[@k='county']")[0]
                val=county.get('v')
                clist=counties.setdefault(val,list())
                clist.append(child)
                child.remove(county)
            except:
                print(county)
        else:
            items[child.tag][child.attrib['id']]=child
    # save data for each county
    for county,relations in counties.items():
        ways=list()
        nodes=list()
        newroot=ElementTree.Element(osm.tag, osm.attrib)
        for relation in relations:
            for member in relation.findall("./member"):
                wid=member.attrib['ref']
                way=items['way'][wid]
                ways.append(way)
                for nd in way.findall("./nd"):
                    nid=nd.attrib['ref']
                    node=items['node'][nid]
                    newroot.append(node)
        for way in ways:
            newroot.append(way)
        for relation in relations:
            newroot.append(relation)
        tree=ElementTree.ElementTree(newroot)
        filepath=os.path.join(args.target, '{}.osm'.format(county.lower()))
        tree.write(open(filepath, 'w'), encoding='unicode')