import csv
import argparse

wikidata=dict()
with open("wikidata.csv") as wiki:
    rdr=csv.reader(wiki)
    for row in rdr:
        if len(row)==5:
            item,title,label,county,gnis=row
            item=item[len("http://www.wikidata.org/entity/"):]
            wikidata[gnis]=item,title

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Process GNIS pipe separated file for use with OGR.')
    parser.add_argument('infile',
                        help='Input file name')
    parser.add_argument('outfile',
                        help='Output file name')
    args = parser.parse_args()
    with open(args.infile) as inf:
        reader=csv.reader(inf, delimiter="|")
        with open(args.outfile, 'w') as ouf:
            writer=csv.writer(ouf, delimiter="\t")
            header=next(reader)
            header[0]="FeatureName"
            if header[-1]=="":
                header.pop(-1)
            header.append("wikidata")
            header.append("wikipedia")
            idcol=header.index("ID")
            writer.writerow(header)
            for row in reader:
                # skip problematic duplicate.
                if row[idcol]=="1625796":
                    continue
                if row[idcol] in wikidata:
                    item,title=wikidata[row[idcol]]
                    row.append(item)
                    if title != "":
                        title="en:{}".format(title)
                    row.append(title)
                else:
                    row.append("")
                    row.append("")
                writer.writerow(row)