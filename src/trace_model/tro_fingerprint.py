#!/usr/bin/env python3

from hashlib import sha256
import os, glob, argparse

def compute_fingerprint(arg_dir, arg_file):

    # All input files
    file_paths = []
    if arg_dir != None:
        for dir in arg_dir.split(","):
            for path in glob.glob(dir + "/**/*", recursive=True): # Include files in sub-directories as well
                if not os.path.isdir(path): # Exclude directories
                    file_paths.append(path)
    if arg_file != None:
        file_paths.extend(arg_file.split(","))

    # Compute digest per file and concat in alphabetical order
    digests = []
    for file_path in file_paths:
        with open(file_path, "rb") as fin:
            digests.append(sha256(fin.read()).hexdigest())
    digest = "".join(sorted(digests))

    # Fingerprint
    fingerprint = sha256(digest.encode("utf-8")).hexdigest()

    return fingerprint

def cli():
    # Parse input
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", "-d", help="Directories of the data (list[str] | str ): please use comma (no space) to split multiple directories (e.g. dir1,dir2,dir3).")
    parser.add_argument("--file", "-f", help="Files of the data (list[str] | str ): please use comma (no space) to split multiple file paths (e.g. file1,file2,file3).")
    parser.add_argument("--expectedfingerprint", "-ef", help="Expected fingerprint (str).")
    arg_dir, arg_file, arg_ef = parser.parse_args().dir, parser.parse_args().file, parser.parse_args().expectedfingerprint

    if not (arg_dir or arg_file):
        parser.error("No action requested. Please add input: --dir OR --file.")
    fingerprint = compute_fingerprint(arg_dir, arg_file)
    # If --expectedfingerprint is not specified,
    # print the fingerprint of the given directories and/or files directly.
    if not arg_ef:
        print(fingerprint)
    # If --expectedfingerprint is specified,
    # we need to validate the fingerprint based on the given field and print True or False.
    else:
        print(fingerprint == arg_ef)

if __name__ == '__main__':
    cli()
