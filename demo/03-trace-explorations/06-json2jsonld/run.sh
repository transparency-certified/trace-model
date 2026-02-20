#!/usr/bin/env bash

CONTEXT1_FILE_PATH=data/context1.csv
CONTEXT2_FILE_PATH=data/context2.csv
CONTEXT3_FILE_PATH=data/context3.csv
JSON_FILE_PATH=data/tro.json
JSONLD_FILE_PATH=products/tro.jsonld

# ------------------------------------------------------------------------------

bash_cell json2jsonld << END_CELL

python3 << END_PYTHON

from pyld import jsonld
import pandas as pd
import numpy as np
import json

def process_id(value):
    return str(value).strip()

def update_dict(data, keys, cm):

    # Unpack context mappings
    cm1, cm2, cm3 = cm

    # TYPE 1
    # e.g., {"trp": 1, "trpAttribute": 1} => {"@id": "trp/1/attribute/1" }
    for item in cm1:
        k1, k2 = item["k1"], item["k2"]
        if (k1 in keys) and (k2 in keys):
            data["@id"] = item["id"].format(id1=process_id(data[k1]), id2=process_id(data[k2]))
            data.pop(k1)
            data.pop(k2)

    # TYPE 2
    # e.g., {"composition": 1, "hasArtifact": {"artifact": 1}} OR {"composition": 1, "hasArtifact": [{"artifact": 1}]} 
    # => {"composition": 1, "hasArtifact": {"@id": "composition/1/artifact/1"}} OR {"composition": 1, "hasArtifact": [{"@id": "composition/1/artifact/1"}]}
    for item in cm2:
        k1, k2, k3 = item["k1"], item["k2"], item["k3"]
        if (k1 in keys) and (k2 in keys):
            if isinstance(data[k2], dict):
                data[k2]["@id"] = item["id"].format(id1=process_id(data[k1]), id2=process_id(data[k2][k3]))
                data[k2].pop(k3)
            else:
                for idx, artifact in enumerate(data[k2]):
                    data[k2][idx]["@id"] = item["id"].format(id1=process_id(data[k1]), id2=process_id(artifact[k3]))
                    data[k2][idx].pop(k3)
    
    # TYPE 3
    # one-to-one mappings based on context3.csv
    for key in cm3.keys():
        if key in keys:
            if isinstance(cm3[key]["idPrefix"], str):
                data[cm3[key]["rdfTerm"]] = cm3[key]["idPrefix"] + process_id(data.pop(key))
            else:
                data[cm3[key]["rdfTerm"]] = data.pop(key)
    
    return data

def traverse_json(obj, cm):
    if isinstance(obj, list):
        for item in obj:
            traverse_json(item, cm)
    elif isinstance(obj, dict):
        keys = obj.keys()
        obj = update_dict(obj, keys, cm)
        for k, v in obj.items():
            if isinstance(v, (list, dict)):
                traverse_json(v, cm)
    return obj

# Load a TRO JSON Declaration
with open('${JSON_FILE_PATH}', 'r', encoding='utf-8') as fin:
    content = fin.read()
json_content = json.loads(content)

# Load the context mappings
cm1 = pd.read_csv('${CONTEXT1_FILE_PATH}').to_dict(orient='records')
cm2 = pd.read_csv('${CONTEXT2_FILE_PATH}').to_dict(orient='records')
cm3 = pd.read_csv('${CONTEXT3_FILE_PATH}', index_col='key').T.to_dict(orient='dict')
cm = [cm1, cm2, cm3]

# Traverse and update it recursively
content = traverse_json(json_content, cm)

# Add context
jsonld = {
    "@context": [{
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "trov": "https://w3id.org/trace/2023/05/trov#",
        "@base": "https://github.com/transparency-certified/trace-model/tree/master/02-tro-examples/03-skope-/"
    }]
}

jsonld["@graph"] = [content]

with open('${JSONLD_FILE_PATH}', 'w', encoding='utf-8') as fout:
     json.dump(jsonld, fout, indent=2)

END_PYTHON

END_CELL

# ------------------------------------------------------------------------------
