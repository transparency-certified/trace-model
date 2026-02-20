from hashlib import sha256
import pandas as pd
import os, glob, argparse

def compute_fingerprint_state(arg_dir, arg_file, arg_c):

    # All input files
    file_paths = []
    if arg_dir != None:
        for dir in arg_dir.split(","):
            for path in sorted(glob.glob(dir + "/**/*", recursive=True)): # Include files in sub-directories as well
                if not os.path.isdir(path): # Exclude directories
                    file_paths.append(path)
    if arg_file != None:
        file_paths.extend(arg_file.split(","))

    # Compute digest per file and concat in alphabetical order
    digests = []
    for file_path in file_paths:
        with open(file_path, "rb") as fin:
            digests.append(sha256(fin.read()).hexdigest())
    
    # Create a dataframe with two columns: file_path and digest
    fingerprint_state = pd.DataFrame({"file_path": file_paths, arg_c: digests})

    return fingerprint_state

def cli():
    # Parse input
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", "-d", help="Directories of the data (list[str] | str ): please use comma (no space) to split multiple directories (e.g. dir1,dir2,dir3).")
    parser.add_argument("--file", "-f", help="Files of the data (list[str] | str ): please use comma (no space) to split multiple file paths (e.g. file1,file2,file3).")
    parser.add_argument("--colname", "-c", choices= ["before", "after"], help="Column name to be shown in the fingerprint_state.csv file: before or after")
    parser.add_argument("--output", "-o", help="Output file path.")
    arg_dir, arg_file, arg_o, arg_c = parser.parse_args().dir, parser.parse_args().file, parser.parse_args().output, parser.parse_args().colname
    
    if not (arg_dir or arg_file):
        parser.error("No action requested. Please add input: --dir OR --file.")
    if not arg_o:
        parser.error("Missing output file path. Please add output file path: --output.")
    if not arg_c:
        parser.error("Missing column name of the digest. Please add column name: --colname.")
    fingerprint_state = compute_fingerprint_state(arg_dir, arg_file, arg_c)
    fingerprint_state.to_csv(arg_o, index=False)


if __name__ == '__main__':
    cli()
