#!/usr/bin/env python3

import argparse

def format_string(string, convert_flag):
    # Convert multiple lines to one line
    if convert_flag == "MULTI2ONE":
        formatted_string = string.replace("\n", "\\n")
    # Convert one line to multiple lines
    else: # ONE2MULTI
        formatted_string = string.replace("\\n", "\n")
    return formatted_string

def cli():

    # Parse input
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", "-f", help="File path ( str )")
    parser.add_argument("--string", "-s", help="Raw string ( str )")
    parser.add_argument("--convertflag", "-cf", choices=["MULTI2ONE", "ONE2MULTI"], help="Convert flag. It must be MULTI2ONE or ONE2MULTI.")
    arg_file, arg_string, arg_convertflag = parser.parse_args().file, parser.parse_args().string, parser.parse_args().convertflag

    if not (arg_file or arg_string):
        parser.error("No action requested. Please add input: --file OR --string.")
    if arg_file and (not arg_string):
        with open(arg_file, encoding="utf-8", mode="r") as fin:
            string = fin.read()
    if (not arg_file) and arg_string:
        string = arg_string
    if arg_file and arg_string:
        parser.error("Only support one type of input per time. Please add --file OR --string.")
    formatted_string = format_string(string, arg_convertflag)
    print(formatted_string)

if __name__ == '__main__':
    cli()
