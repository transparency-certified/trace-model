#!/usr/bin/env bash

# paths to data files
COMMON=../common

# ------------------------------------------------------------------------------

bash_cell import jsonld << END_CELL

# Import TRO and TRS as JSON-LD and export as N-TRIPLES
geist-p create --dataset kb --inputformat json-ld --inputfile ${COMMON}/trace-vocab.jsonld --infer owl

END_CELL

# ------------------------------------------------------------------------------

bash_cell export ntriples << END_CELL

# Export kb dataset as N-TRIPLES
geist-p export --dataset kb --outputformat nt | sort | grep trov

END_CELL

# ------------------------------------------------------------------------------

bash_cell query_subclass_vocab << END_CELL

geist-p query --dataset kb << __END_QUERY__

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

bash_cell visualize_subclass_vocab_using_graphviz << END_CELL

geist-p report --outputfile products/query_subclass_vocab --outputformat none --outputformat png --outputformat gv << END_TEMPLATE

    {% template "graphviz.geist" %}
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

    {% gv_graph "subclass_vocab_graph", "BT" %}
    {% gv_title "Subclass Vocab Graph" %}
    {% gv_cluster "subclass" %}

    node[shape=box style="filled" fillcolor="#CCFFCC" peripheries=1 fontname=Courier]
    {% for _, row in query_subclass_vocab.iterrows() %}
        {% gv_edge row["ChildLabel"], row["ParentLabel"] %}
    {% endfor %}

    {% gv_cluster_end %}
    {% gv_end %}

    {% destroy %}

END_TEMPLATE

END_CELL

# ------------------------------------------------------------------------------