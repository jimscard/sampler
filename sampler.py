#! /usr/bin/env python3
import csv
import sys
import os
from hashlib import sha256 
import random
import math
import secrets

def main():
    """
    Main function to process a CSV file provided as a command-line argument.
    It reads the file, randomly samples 25% of its lines (up to a maximum of 25 lines),
    and writes the sampled lines to a new file prefixed with 'samples-'.

    Raises:
        RuntimeError: If the provided file path is outside the current working directory.
    """
    # Check if the filename is provided as a command-line argument
    if len(sys.argv) < 2:
        print('Please provide the filename of the CSV file as an argument')
        return

    # Get the filename from the command-line arguments
    filename = sys.argv[1]
    # Construct the full file path
    filepath = os.getcwd() + '/' + filename

    # Ensure the file path is within the current working directory
    if not os.path.abspath(os.path.realpath(filepath)).startswith(os.getcwd()): # import os
        raise RuntimeError('Filepath falls outside the base directory')
    
    # Open the CSV file for reading, ignoring any errors
    with open(filepath, 'r', errors='ignore') as csv_in: 
        # Define the output file name
        csv_out = "samples-" + filename 
        # Read all lines from the input file
        lines = csv_in.readlines()  # Read the file into a list of lines
        # Seed the random number generator for sampling
        random.seed(secrets.token_bytes(32))
        # Determine the total number of lines
        population = len(lines)
        # Calculate the sample size (25% of total lines or 25, whichever is smaller)
        sample_size = min(math.floor(population * 0.25), 25)
        # Randomly sample the lines
        sample_lines = random.sample(lines, sample_size)  
        
        # Write the sampled lines to the output file
        with open(csv_out, 'w') as f: 
            f.write(''.join(sample_lines))  # Write the sampled lines to a new file
        # Print the result of the sampling process
        print(f"{sample_size} samples out of a population of {population} written to {csv_out}")
if __name__ == "__main__": 
    main()
