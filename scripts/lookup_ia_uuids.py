# This script was used to act as a cache of cnx book uuids and collection ids to be
# used later in cnx-rex-redirects script. The processing time of looking up uuid to 
# colid was too much so I decided to write all these to a file to be used later to
# create the redirects to internet archive

import json

import internetarchive
import requests

cnx_archive_url = "https://archive.cnx.org/content"

colids = [f"{i['identifier'].split('cnx-org-')[-1]}" for i in internetarchive.search_items("cnx-org")]
book_data = []

for id in colids:
    book_item = dict()
    book_item["colid"] = id
    r = requests.get(f"{cnx_archive_url}/{id}")
    r.raise_for_status()

    book_url = r.url
    book_item["uuid"] = book_url.split("/")[-1].split("@")[0]
    book_data.append(book_item)

with open("scripts/output/cnx_user_books.json", "w") as outfile:
    outfile.write(json.dumps(book_data))
        
