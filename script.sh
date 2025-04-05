#!/bin/bash

# This script extracts text content from a specific table element without using a temp file
# Usage: ./script.sh <coin>

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <coin>"
    exit 1
fi

COIN="$1"
START_DATE="2015-01-01"
END_DATE=$(date +%Y-%m-%d)

INPUT_FILE="page.html"
curl -L "https://coincodex.com/crypto/$COIN" -o "$INPUT_FILE"

# Create a single-line version of the file for easier processing
SINGLE_LINE=$(tr '\n' ' ' < "$INPUT_FILE")

# Extract from the specific table tag to the first closing table tag
TABLE_START=$(echo "$SINGLE_LINE" | grep -o -b "<table _ngcontent-coincodex-c876666857[^>]*>" | head -1 | cut -d: -f1)

if [ -z "$TABLE_START" ]; then
    echo "Error: Table with attribute _ngcontent-coincodex-c876666857 not found"
    exit 1
fi

# Get the position of the first </table> after the starting position
SUBSTR=${SINGLE_LINE:$TABLE_START}
TABLE_END_REL=$(echo "$SUBSTR" | grep -o -b "</table>" | head -1 | cut -d: -f1)
TABLE_END=$((TABLE_START + TABLE_END_REL + 8)) # 8 is the length of </table>

# Extract the substring from start to end
TABLE_CONTENT=${SINGLE_LINE:$TABLE_START:$((TABLE_END - TABLE_START))}

# Extract all text elements between > and < from the table content
# Use grep to find patterns, sed to extract the text, and filter empty lines
TEXT_ELEMENTS=$(echo "$TABLE_CONTENT" | grep -o ">[^<]*<" | sed 's/^>//;s/<$//' |
                grep -v "#" | 
                grep -v "^ ([0-9]\+%)" | 
                grep -v "^ (-[0-9]\+%)" | 
                grep -v "^[[:space:]]*$")

# Save all the extracted elements with line numbers
echo "$TEXT_ELEMENTS" > extracted_elements.txt

# Count total non-empty elements
TOTAL=$(echo "$TEXT_ELEMENTS" | wc -l)
echo "Total elements found: $TOTAL"

INPUT_FILE="extracted_elements.txt"
OUTPUT_FILE="stats.csv"

# Write CSV header
echo "Stats,Value" > "$OUTPUT_FILE"

# Initialize a flag to indicate if we're on a stat (first line) or a value (second line).
is_stat=true
stat=""

# Read the input file line by line.
while IFS= read -r line; do
    # Trim leading and trailing whitespace.
    trimmed=$(echo "$line" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
    
    # Skip blank lines.
    if [ -z "$trimmed" ]; then
        continue
    fi

    if $is_stat; then
        # This line is the statistic.
        stat="$trimmed"
        is_stat=false
    else
        # This line is the value. Output the CSV line.
        value="$trimmed"
        # Enclose in quotes to handle commas or spaces.
        echo "\"$stat\",\"$value\"" >> "$OUTPUT_FILE"
        # Reset for the next pair.
        is_stat=true
    fi
done < "$INPUT_FILE"

echo "CSV file created as $OUTPUT_FILE"

# Construct URL
URL="https://www.coingecko.com/price_charts/export/$COIN/usd.csv?from=$START_DATE&to=$END_DATE"

# Filename for the CSV
FILE_NAME="prices.csv"

# Use curl to download and save CSV
curl -L "$URL" -o "$FILE_NAME"

echo "historical data saved" 



