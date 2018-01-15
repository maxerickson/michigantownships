import csv
import argparse

mismatched_labels={
"City of Mount Clemens":"City of Mt Clemens",
"City of Mount Morris":"City of Mt Morris",
"City of Mount Pleasant":"City of Mt Pleasant",
"Village of Ovid":"City of Ovid",
"City of Sault Ste. Marie":"City of Sault Ste Marie",
"City of Saint Clair":"City of St Clair",
"City of Saint Clair Shores":"City of St Clair Shores",
"City of Saint Ignace":"City of St Ignace",
"City of Saint Johns":"City of St Johns",
"City of Saint Joseph":"City of St Joseph",
"City of Saint Louis":"City of St Louis",
"City of the Village of Grosse Pointe Shores":"City of The Village of Grosse Pointe Shores A Michigan City",
"City of the Village of Clarkston":"City of Village of Clarkston",
"City of Douglas":"City of Village of Douglas",
"Township of Sims":"Sims Township",
"Township of Saint James":"St James Township",
"Township of Pointe Aux Barques":"Pointe Aux Barques Township",
"Township of Port Austin":"Port Austin Township",
"Township of Lake":"Lake Township",
"Township of Gore":"Gore Township",
"Township of Caseville":"Caseville Township",
"Township of Rubicon":"Rubicon Township",
"Township of Fairhaven":"Fairhaven Township",
"Township of Houghton":"Houghton Township",
"Township of Eagle Harbor":"Eagle Harbor Township",
"Township of Leelanau":"Leelanau Township",
"Township of Leland":"Leland Township",
"Township of Suttons Bay":"Suttons Bay Township",
"Township of Glen Arbor":"Glen Arbor Township"}


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
            writer=csv.writer(ouf)
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
                # Fix differening labels.
                if row[0] in mismatched_labels:
                    row[0]=mismatched_labels[row[0]]
                writer.writerow(row)
