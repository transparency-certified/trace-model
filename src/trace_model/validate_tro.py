#!/usr/bin/env python3

from pyshacl import validate
from rdflib import Graph
import pygraphviz as pgv
import pandas as pd
import argparse, os

mappings={
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf#",
    "http://www.w3.org/2000/01/rdf-schema#": "rdfs#",
    "https://w3id.org/trace/2023/05/trov#": "trov#",
    "https://github.com/transparency-certified/trace-model/tree/master/demo/01-trov-examples/01-two-artifacts-no-trp/": ""
    }

def ensure_dir_exists(file_path):
    dir_path = os.path.split(file_path)[0]
    if (dir_path != '') and (not os.path.isdir(dir_path)):
        os.makedirs(dir_path)
    return

def load_tro_file(file_path, graph_format="json-ld"):
    """
    This function is to load a file with a given format as a RDF Graph object supported by RDFLib
    :param file_path: String. Path of the file
    :param graph_format: Defaults to json-ld. It could be one of {xml, n3, turtle, nt, pretty-xml, trix, trig, nquads, json-ld, hext}
    :return tro_graph: a RDF Graph object supported by RDFLib
    """
    if graph_format not in {"xml", "n3", "turtle", "nt", "pretty-xml", "trix", "trig", "nquads", "json-ld", "hext"}:
        raise ValueError("RDFLib .parse() only supports {xml, n3, turtle, nt, pretty-xml, trix, trig, nquads, json-ld, hext}, but '" + str(format) + "' was given.")
    # Load the file (e.g., a JSON-LD file) as string
    with open(file_path) as fin:
        tro_str = fin.read()
    # Parse string with RDFLib
    tro_graph = Graph()
    tro_graph.parse(data=tro_str, format=graph_format)
    return tro_graph

def validate_tro(tro, tro_schema, data_graph_format="json-ld", shacl_graph_format="ttl", flag=False):
    """
    This function is validate the tro_jsonld_graph with tro_schema
    :param tro: a RDF Graph object supported by RDFLib or a String
    :param tro_schema: a RDF Graph object or a String
    :param data_graph_format: format of tro, default value is json-ld
    :param shacl_graph_format: format of tro_schema, default value is ttl
    :return results_graph: a RDF Graph object showing all errors
    """

    r = validate(data_graph=tro,
            shacl_graph=tro_schema,
            data_graph_format=data_graph_format,
            shacl_graph_format=shacl_graph_format,
            inference="rdfs",
            debug=True)
    conforms, results_graph, results_text = r

    if flag:
        print(results_text)

    return results_graph

def extract_errors(results_graph):
    """
    This function is to extract the most important errors
    Ideally, all errors will be fixed once solve these errors
    :param results_graph: a RDF Graph object showing all errors
    :return errors: a Pandas data frame with node, msg, and path columns
    """

    q = """
        PREFIX : <http://www.w3.org/ns/shacl#>

        SELECT ?focus ?msg ?path
        WHERE {
            ?curr_node :focusNode ?focus .
            ?curr_node :resultMessage ?msg .
            ?curr_node :resultPath ?path.
            OPTIONAL { ?curr_node :detail ?child_node. }
            FILTER (!bound(?child_node))
        }
        ORDER BY ?focus ?msg ?path
    """
    rows = []
    for r in results_graph.query(q):
        rows.append(r)
    errors = pd.DataFrame(rows, columns=["node", "msg", "path"]).replace(mappings, regex=True).drop_duplicates()
    return errors

def process_graph(tro_graph, mappings, errors):
    """
    This function is to process a RDF Graph object:
        (1) make the node name shorter
        (2) export as a Pandas data frame
        (3) add suggested nodes to be updated to the errors data frame
    :param tro_graph: a RDF Graph object
    :param mappings: a dictionary used to make the node name shorter
    :param errors: a Pandas data frame with node, msg, and path columns
    :return tro_graph_processed: a Pandas data frame
    :return errors_with_suggested_nodes: a Pandas data frame with node, msg, and target columns, where target column denotes suggested nodes to be updated
    """
    # Query the imported triples in tro_graph
    q = """
            SELECT ?s ?p ?o
            WHERE {
                ?s ?p ?o
            }
            ORDER BY ?s ?p ?o
        """
    rows = []
    for r in tro_graph.query(q):
        rows.append(r)
    tro_graph_processed = pd.DataFrame(rows, columns=["source", "label", "target"]).replace(mappings, regex=True)
    errors_with_suggested_nodes = errors.merge(tro_graph_processed, how="inner", left_on=["node", "path"], right_on=["source", "label"])[["node", "msg", "target"]]
    return tro_graph_processed, errors_with_suggested_nodes

def visualize_graph_as_dot(tro_graph_processed, errors_with_suggested_nodes):
    # Create a directed graph
    G = pgv.AGraph(directed=True)
    # Add nodes and edges
    for _, row in tro_graph_processed.iterrows():
        G.add_node(row["source"], shape="box", style="filled, rounded", fillcolor="#b3e2cd")
        G.add_node(row["target"], shape="box", style="filled, rounded", fillcolor="#b3e2cd")
        G.add_edge(row["source"], row["target"], label=row["label"])
    for _, row in errors_with_suggested_nodes[["node", "msg"]].drop_duplicates().iterrows():
        G.add_node(row["node"], shape="box", style="filled, rounded", fillcolor="#fdccac")
        G.add_node(row["msg"], shape="box", style="filled, rounded, dashed", fillcolor="#fdccac")
        G.add_edge(row["node"], row["msg"], label="ErrorMsg", style="dashed")
    # Suggested nodes to be updated
    for suggested_node in errors_with_suggested_nodes["target"].dropna().unique():
        G.add_node(suggested_node, shape="box", style="filled, rounded", fillcolor="#cbd5e8")
    return G

def report_graph_as_txt(errors_with_suggested_nodes):
    report_text = ""
    for _, row in errors_with_suggested_nodes.groupby(["node", "msg"])["target"].agg(list).reset_index().iterrows():
        report_text = report_text + "Node: {node} \nError Message: {msg}\nSuggested Node(s) to be Updated: {suggested_node}\n\n".format(node=row["node"], msg=row["msg"], suggested_node=", ".join(row["target"]))
    return report_text

def cli():
    # Parse input
    parser = argparse.ArgumentParser()
    parser.add_argument("--showerrors", "-se", default=False, help="Show all errors.")
    parser.add_argument("--file", "-f", help="File(s) of the TRO Declarations to be validated (list[str] | str ): please use comma (no space) to split multiple file paths (e.g. file1,file2,file3).")
    parser.add_argument("--schema", "-s", help="Schema of the TRO Declaration (str): path of the file.")
    parser.add_argument("--fileformat", "-ff", help="File format(s) of the TRO Declarations to be validated (list[str] | str ). Orders should be consistent with the input of --file. Default format is json-ld. If all input files have the same format, only need to write once.")
    parser.add_argument("--schemaformat", "-sf", default="ttl", choices=["xml", "n3", "turtle", "nt", "pretty-xml", "trix", "trig", "nquads", "json-ld", "hext"], help="File format of the schema (str). Default format is ttl.")
    parser.add_argument("--output", "-o", help="File(s) of the validation report without extension (list[str] | str ). If no value, then output will be a string. Please use comma (no space) to split multiple file paths (e.g. file1,file2,file3).")
    parser.add_argument("--outputformat", "-of", help="File format(s) of the output, validation report (list[str] | str ).  Orders should be consistent with the input of --output. Default format is txt. Each item can only be one of {txt,png,gv}. Please use comma (no space) to split multiple formats (e.g. format1,format2,format3). If all output files have the same format, only need to write once.")
    arg_showerrors, arg_file, arg_schema, arg_fileformat, arg_schemaformat, arg_outputformat, arg_output = parser.parse_args().showerrors, parser.parse_args().file, parser.parse_args().schema, parser.parse_args().fileformat, parser.parse_args().schemaformat, parser.parse_args().outputformat, parser.parse_args().output

    if not arg_file:
        parser.error("File(s) of the TRO Declaration to be validated are missing. Please add: --file.")
    if not arg_schema:
        parser.error("Schema file is missing. Please add: --schema.")
    file_paths = arg_file.split(",")
    num_files = len(file_paths)
    output_paths = [None] * num_files if not arg_output else arg_output.split(",")
    file_formats = ["json-ld"] * num_files if not arg_fileformat else arg_fileformat.split(",")
    output_formats = ["txt"] * num_files if not arg_outputformat else arg_outputformat.split(",")
    if len(file_formats) == 1:
        file_formats = file_formats * num_files
    if len(output_formats) == 1:
        output_formats = output_formats * num_files

    if num_files != len(file_formats) or num_files != len(output_formats) or num_files != len(output_paths):
        raise ValueError("Please make sure the number of input files (and input formats) equals to the number of output files (and output formats): check the value of --file, --fileformat, --output, --outputformat.")

    for file_path, file_format, output_path, output_format in zip(file_paths, file_formats, output_paths, output_formats):
        # Load TRO Declaration
        tro_graph = load_tro_file(file_path, graph_format=file_format)
        # Validate the TRO Declaration
        results_graph = validate_tro(tro_graph, arg_schema, data_graph_format=file_format, shacl_graph_format=arg_schemaformat, flag=arg_showerrors)
        # Find the most important errors
        errors = extract_errors(results_graph)
        # Find the suggested error nodes
        (tro_graph_processed, errors_with_suggested_nodes) = process_graph(tro_graph, mappings, errors)
        # Output
        if output_format not in ["txt", "png", "gv"]:
            raise ValueError("The output file format can only be one of {txt, png, gv}, but " + str(output_format) + " was given. Please check --outputformat.")
        
        output_path = output_path + "." + output_format if output_path else None
        if output_path:
            ensure_dir_exists(output_path)
        if output_format == "png" or output_format == "gv":
            G = visualize_graph_as_dot(tro_graph_processed, errors_with_suggested_nodes)
            if output_format == "png":
                G.draw(output_path, prog="dot")
            else: # gv
                G.write(output_path)
        else:
            report_text = report_graph_as_txt(errors_with_suggested_nodes)
            if not output_path:
                # If NO --output, print a string
                print(report_text)
            else:
                with open(output_path, mode="w", encoding="utf-8") as fout:
                    fout.write(report_text)

if __name__ == '__main__':
    cli()