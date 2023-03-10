#!/usr/bin/env python
"""
Stub function and module used as a setuptools entry point.
Based on augur's __main__.py and setup.py
"""

import getopt
import sys
import json
import pandas as pd
import Bio.AlignIO as AlignIO
from . import NextcladeTree
from . import attach_new_sequences
from . import write_new_json

def get_args(argv):
    message = """treebuilder -t <ref_tree_json> -d <new_sequences_data_ndjson> -r <reference_sequence_fasta>,
            if no reference sequence is provided, the length of the reference sequence will be set to 1"""
    reference_tree = None
    data = None
    reference_seq = None
    # Get the arguments from the command-line except the filename
    try:
        # Define the getopt parameters
        opts, args = getopt.getopt(argv[1:], 'ht:d:r:', ['ref_tree', 'data', 'ref_seq'])
    except getopt.GetoptError:
        # Print something useful
        print (message)
        sys.exit(2)
    if len(opts) <2:
        print (message)
        sys.exit()
    for opt, arg in opts:
        if opts == '-h':
            print (message)
            sys.exit()
        elif opt in ("-t", "--ref_tree"):
            reference_tree = arg
        elif opt in ("-d", "--data"):
            data = arg
        elif opt in ("-r", "--ref_seq"):
            reference_seq = arg
        else:
            print (message)
            sys.exit()

    return reference_tree, data, reference_seq


# Entry point for setuptools-installed script and bin/augur dev wrapper.
def main():
    ref_tree_json, new_seq_ndjson, ref_seq_fasta = get_args(sys.argv)
    # ref_tree_json = "test/tree.json" 
    # new_seq_ndjson = "test/nextclade.ndjson" 
    # ref_seq_fasta = "test/reference.fasta" 
    # Opening JSON file
    tree_json_as_dict = json.load(open(ref_tree_json))

    #Get length of reference sequence
    if ref_seq_fasta:
        ref_seq = AlignIO.read(ref_seq_fasta, 'fasta') 
        len_ref_seq = len(ref_seq[0].seq)
        print("length of reference sequence is: "+ str(len_ref_seq))
    else:
        len_ref_seq = 1

    nc_tree = NextcladeTree(tree_json_as_dict, seq_length=len_ref_seq)
    #import ipdb; ipdb.set_trace()

    #get new sequences with attachment points and private mutations
    df = pd.read_json(new_seq_ndjson, lines=True)
    sequences_df = df[['seqName', 'nearestNodeId', 'privateNucMutations']]

    ## attach sequences to tree
    attach_new_sequences(nc_tree, sequences_df)

    write_new_json("output_tree.json", nc_tree.tree, tree_json_as_dict)


# Run when called as `python -m treetime`, here for good measure.
if __name__ == "__main__":
    main()