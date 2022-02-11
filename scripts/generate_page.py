import argparse, sys, json, requests, os

def parse_file(file_path):

    if not os.path.exists(file_path):
        raise Exception("File not found at path " + file_path)
    pub_id_list = []
    with open(file_path, 'r') as f:
        pub_id_list = [line.strip() for line in f]
    return pub_id_list

def _extract_data(pub_id, pub):
    url = "https://www.ncbi.nlm.nih.gov/pubmed/" + pub_id
    data = {'url': url, 'title': pub['title'].encode('utf8'), 'author': pub['authors'][0]['name'].encode('utf8'), 'year': pub['pubdate'].split(" ")[0] , 'journal': pub['source'].encode('utf8'), 'id': pub_id}
    return data

def get_data(pubmed_list):
    string = ",".join(pubmed_list)
    # use Json because it's easier to parse..
    citations = []
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=" + string
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.content.decode('utf-8'))
        for pub_id, pub in data['result'].items():
            if not pub_id == "uids":
                citations.append(_extract_data(pub_id, pub))

    return sorted(citations, key = lambda i: i['id'], reverse=True)

def write_file(pubmed_data):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    spacing = "                  "
    text = ""

    for pub in pubmed_data:
        text += spacing + "<li><b>{} <i>et al.,</i> {}, {}, </b><a target='_blank' href='{}'>{}</a></li>\n".format(pub['author'], pub['year'], pub['journal'], pub['url'], pub['title'])

    f = open(os.path.join(__location__, "citing_base.html"), "r")
    contents = f.readlines()
    f.close()
    index = 40
    contents.insert(index, text)
    f = open(os.path.join(__location__,"citing.html"), "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate template file for citations')
    parser.add_argument( 'file', action = 'store', type = str, help = 'Path to file' )
    args = parser.parse_args()

    pubmed_list = parse_file(args.file)
    pubmed_data = get_data(pubmed_list)
    write_file(pubmed_data)
