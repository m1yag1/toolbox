# This is script was written to take a csv file of dns entries for cnx.org and
# prepare them for a terragrunt config

import os

import jinja2

from toolbox.csv import get_rows

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
INPUT_PATH = os.path.join(SCRIPT_PATH, "input")
OUTPUT_PATH = os.path.join(SCRIPT_PATH, "output")

environment = jinja2.Environment()
template = environment.from_string("""
terraform {
  source = "git::git@github.com:openstax/ce-infra.git//terraform/modules/route53-records"
}

include {
  path = find_in_parent_folders()
}

dependency "route53" {
  config_path = "../route53-zone-cnx.org"
}

inputs = {
  zone_id = dependency.route53.outputs.main_hosted_zone_id
  records = [
    {% for record in records %}
    {
        name = "{{ record.name }}",
        type = "{{ record.type }}",
        ttl = 300,
        records = [
            "{{ record.data }}"
        ]
    },
    {%- endfor %}
  ]
}
""")

csv_filepath = os.path.join(INPUT_PATH, "cnx-org-dns-records.csv")
records = []
errors = []

records_data = [row for row in get_rows(csv_filepath)]
print(f"{len(records_data)} dns records to process")

for r in records_data:
    name = r["Name"]
    record_type = None

    if "MX" in r["Type"]:
        if not name:
            name = r["Data"].split(" ")[-1] 
        record_type = "MX"
    
    if "TXT" in r["Type"]:
        record_type = "TXT"
    
    if "PTR" in r["Type"]:
        record_type = "PTR"
    
    if "CNAME" in r["Type"]:
        record_type = "CNAME"
    
    if "A Record" in r["Type"]:
        record_type = "A"
        if not name:
            name = "@"
    
    if record_type:
        if not name:
            name = r["Data"]
        records.append({"name": name, "type": record_type, "data": r["Data"]})
    else:
        errors.append({"name": r["Name"], "type": record_type, "data": r["Data"]})
        continue

print(f"{len(records)} DNS records processed and {len(errors)} records skipped.")

with open(os.path.join(OUTPUT_PATH, "terragrunt.hcl"), "w") as outfile:
    outfile.write(template.render(records=records))
