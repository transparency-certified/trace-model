#!/usr/bin/env bash

source ../common/query-tro.sh

# ------------------------------------------------------------------------------

bash_cell tro_report << END_CELL

geist report --outputroot products << END_TEMPLATE

{%- use "templates.geist" %}
{%- create %} tro/tro.jsonld {% endcreate %}

{%- html "report.html" %}
{%- head "TRO Report" %}

    <body>
        <h1>TRO Report</h1>
        <h3>This Transparent Research Object:</h3>
        {%- map isfilepath=False, mappings="mappings.json" as query_tro_shorten %} {% query_tro_str %} {% endmap %}
        {%- set query_tro = query_tro_shorten | json2df %}
        {% for _, row in query_tro.iterrows() %}
        <u>{{ row["tro_name"] }}</u>
        <ul>
            <li>TRO ID: {{ row["tro_id"] }}</li>
            <li>TRO Description: {{ row["tro_descr"] }}</li>
            <li>Digital artifacts: {{ row["num_of_artifacts"] }}</li>
            <li>Artifact artifact arrangements: {{ row["num_of_arrs"] }}</li>
            <li>Trusted Research Performances (TRPs): {{ row["num_of_trps"] }}</li>
        </ul>
        {% endfor %}

        <h3>Trusted Research System:</h3>
        {%- map isfilepath=False, mappings="mappings.json" as query_trs_shorten %} {% query_trs_str %} {% endmap %}
        {%- set query_trs = query_trs_shorten | json2df %}
        {% for _, row in query_trs.iterrows() %}
        <u>{{ row["trs_name"] }}</u>
        <ul>
            <li>TRS ID: {{ row["trs_id"] }}</li>
            <li>TRS Description: {{ row["trs_descr"] }}</li>
            <li>Capabilities: {{ row["num_of_capabilities"] }} (see below)</li>
        </ul>
        {% endfor %}
        {%- table mappings="mappings.json" %}{% query_trs_capability_str %}{% endtable %}

        <h3>Trusted Research Performances (TRPs) and Arrangements:</h3>
        {% img src="trp.svg" %}
            {%- gv_graph "trp", "LR" %}
            nodesep=0.6
            node[shape=box style="filled, rounded" fillcolor="#b3e2cd" peripheries=1 fontname=Courier]
            {%- map isfilepath=False, mappings="mappings.json" as query_trp_shorten %} {% query_trp_str %} {% endmap %}
            {%- set query_trp = query_trp_shorten | json2df %}
            {% for _, row in query_trp.iterrows() %}
                {% gv_labeled_edge row["in"], row["out"], row["trp"] %}
            {% endfor %}
            {% gv_end %}
        {% endimg %}

        <h3>Artifacts:</h3>
        {%- table mappings="mappings.json" %}{% query_artifact_str %}{% endtable %}

        <h3>Artifacts by Arrangement:</h3>
        {%- query isfilepath=False as query_arrangement_str %}
            SELECT DISTINCT ?arrangement (STR(?arrangement) AS ?id) ?name ?descr
            WHERE {
                ?tro          rdf:type    trov:TransparentResearchObject .
                ?tro          trov:hasArrangement ?arrangement .
                ?arrangement  rdfs:label    ?name .
                ?arrangement  rdfs:comment  ?descr .
            }
            ORDER BY ?arrangement
        {% endquery %}

        {%- map isfilepath=False, mappings="mappings.json", on="id" as query_arrangement_shorten %} {{ query_arrangement_str }} {% endmap %}
        {%- set query_arrangement = query_arrangement_shorten | json2df %}
        {% for idx, row in query_arrangement.iterrows() %}
        <u>{{ row["name"] }}</u>
        <ul>
            <li>Arrangement ID: {{ row["id"] }}</li>
            <li>Arrangement Description: {{ row["descr"] }}</li>
            <li>Digital artifacts: {%- table mappings="mappings.json" %}{% query_artifacts_by_arrangement_str row["arrangement"] %}{% endtable %}</li>
        </ul>
        {% endfor %}

</body>
{% endhtml %}

{%- destroy %}

END_TEMPLATE

END_CELL

# ------------------------------------------------------------------------------
