#!/usr/bin/env bash

# paths to data files
COMMON=../common

# ------------------------------------------------------------------------------

bash_cell import jsonld << END_CELL

# Import TRO and TRS as JSON-LD and export as N-TRIPLES
geist destroy --dataset kb --quiet
geist create --dataset kb --inputformat json-ld --inputfile ${COMMON}/trace-vocab.jsonld --infer owl

END_CELL

# ------------------------------------------------------------------------------

bash_cell export ntriples << END_CELL

# Export kb dataset as N-TRIPLES
geist export --dataset kb --outputformat nt | sort | grep trov

END_CELL

# ------------------------------------------------------------------------------

bash_cell query_subclass_vocab << END_CELL

geist query --dataset kb << __END_QUERY__

    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?ChildLabel ?ParentLabel
    WHERE {
        ?ParentClass    rdf:type        rdfs:Class ;
                        rdfs:label      ?ParentLabel .
        
        ?ChildClass     rdfs:subClassOf ?ParentClass ;
                        rdf:type        rdfs:Class ;
                        rdfs:label      ?ChildLabel .

        FILTER (?ChildLabel != ?ParentLabel)
    }
    ORDER BY ?ChildLabel ?ParentLabel

__END_QUERY__

END_CELL

# ------------------------------------------------------------------------------

bash_cell test_jinja_include << END_CELL

geist report << END_TEMPLATE

    {% include "base.gv" %}

END_TEMPLATE

END_CELL

# ------------------------------------------------------------------------------

bash_cell test_jinja_extends << END_CELL

geist report << END_TEMPLATE

    {% extends "base.gv" %}
    {% block gv_graph_name %}subclass_vocab_graph{% endblock %}
    {% block gv_title %}Subclass Vacab Graph{% endblock %}

END_TEMPLATE

END_CELL

# ------------------------------------------------------------------------------

bash_cell visualize_subclass_vocab_using_jinja_import << END_CELL

geist report << END_TEMPLATE

    {% import "graphviz.jinja" as gv_macros %}
    {% query isfilepath=False as query_subclass_vocab_str %}
        SELECT DISTINCT ?ChildLabel ?ParentLabel
        WHERE {
            ?ParentClass    rdf:type        rdfs:Class ;
                            rdfs:label      ?ParentLabel .
            
            ?ChildClass     rdfs:subClassOf ?ParentClass ;
                            rdf:type        rdfs:Class ;
                            rdfs:label      ?ChildLabel .

            FILTER (?ChildLabel != ?ParentLabel)
        }
        ORDER BY ?ChildLabel ?ParentLabel
    {% endquery %}
    {% set query_subclass_vocab = query_subclass_vocab_str | json2df %}

    {{ gv_macros.gv_graph("subclass_vocab_graph", "BT") }}
    {{ gv_macros.gv_title("Subclass Vacab Graph") }}
    {{ gv_macros.gv_cluster("subclass") }}

    node[shape=box style="filled" fillcolor="#CCFFCC" peripheries=1 fontname=Courier]
    {% for _, row in query_subclass_vocab.iterrows() %}
        {{ gv_macros.gv_edge(row["ChildLabel"], row["ParentLabel"]) }}
    {% endfor %}

    {{ gv_macros.gv_cluster_end() }}
    {{ gv_macros.gv_end() }}

END_TEMPLATE

END_CELL

# ------------------------------------------------------------------------------

bash_cell visualize_subclass_vocab_using_geist << END_CELL

geist report << END_TEMPLATE
    
{%- use "graphviz.geist" %}
{%- query isfilepath=False as query_subclass_vocab_str %}
    SELECT DISTINCT ?ChildLabel ?ParentLabel
    WHERE {
        ?ParentClass    rdf:type        rdfs:Class ;
                        rdfs:label      ?ParentLabel .
        
        ?ChildClass     rdfs:subClassOf ?ParentClass ;
                        rdf:type        rdfs:Class ;
                        rdfs:label      ?ChildLabel .

        FILTER (?ChildLabel != ?ParentLabel)
    }
    ORDER BY ?ChildLabel ?ParentLabel
{% endquery %}
{%- set query_subclass_vocab = query_subclass_vocab_str | json2df %}

{%- html "report.html" %}
{%- head "Geist Report" %}

    <body>
        <h1>Geist Report</h1>
        <p>This report shows part of the vocabulary of TRACE.
        <h3>1. Graph Demo</h3>
        <h4>(1) PNG</h4>
        {% img src="products/img.jpg" %}
            {%- gv_graph "subclass_vocab_graph", "BT" %}
            {%- gv_title "Subclass Vocab Graph" %}
            {%- gv_cluster "subclass" %}

            node[shape=box style="filled" fillcolor="#CCFFCC" peripheries=1 fontname=Courier]
            {% for _, row in query_subclass_vocab.iterrows() %}
                {% gv_edge row["ChildLabel"], row["ParentLabel"] %}
            {% endfor %}

            {% gv_cluster_end %}
            {% gv_end %}
        {% endimg %}

        <h4>(2) SVG</h4>
        {% img src="products/img.svg" %}
            {%- gv_graph "subclass_vocab_graph", "BT" %}
            {%- gv_title "Subclass Vocab Graph" %}
            {%- gv_cluster "subclass" %}

            node[shape=box style="filled" fillcolor="#CCFFCC" peripheries=1 fontname=Courier]
            {% for _, row in query_subclass_vocab.iterrows() %}
                {% gv_edge row["ChildLabel"], row["ParentLabel"] %}
            {% endfor %}

            {% gv_cluster_end %}
            {% gv_end %}
        {% endimg %}

        <h4>(3) GV</h4>
        {% img src="products/img.gv" %}
            {%- gv_graph "subclass_vocab_graph", "BT" %}
            {%- gv_title "Subclass Vocab Graph" %}
            {%- gv_cluster "subclass" %}

            node[shape=box style="filled" fillcolor="#CCFFCC" peripheries=1 fontname=Courier]
            {% for _, row in query_subclass_vocab.iterrows() %}
                {% gv_edge row["ChildLabel"], row["ParentLabel"] %}
            {% endfor %}

            {% gv_cluster_end %}
            {% gv_end %}
        {% endimg %}
        
         <h3>2. Table Demo</h3>
        {%- table %}
            {{ query_subclass_vocab_str }}
        {% endtable %}
</body>
{% endhtml %}
{%- destroy %}

END_TEMPLATE

END_CELL

# ------------------------------------------------------------------------------
