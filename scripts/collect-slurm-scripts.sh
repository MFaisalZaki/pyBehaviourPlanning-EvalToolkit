#!/bin/bash

# Directory to list files from (can be passed as an argument)
DIRECTORY=${1:-.}

# Output file (can be passed as an argument)
OUTPUT_FILE=${2:-output.txt}

# Ensure the output file is empty
> "$OUTPUT_FILE"

# Find all files in the directory, sort them, and write full paths to the output file
find "$DIRECTORY" -type f | sort > "$OUTPUT_FILE"

echo "Files have been listed and written to $OUTPUT_FILE"
