#!/bin/bash
# Usage: ./scrape_coingecko.sh <coin>
# Example: ./scrape_coingecko.sh ethereum

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <coin>"
    exit 1
fi

COIN="$1"
START_DATE="2015-01-01"
END_DATE=$(date +%Y-%m-%d)

URL="https://www.coingecko.com/en/coins/${COIN}"
OUTPUT_FILE="stats.csv"

# Fetch the page using curl with a common browser User-Agent
HTML=$(curl -s -A "Mozilla/5.0" "$URL")

# Convert HTML to a single line to simplify regex matching
HTML_ONELINE=$(echo "$HTML" | tr '\n' ' ')

# Extract table rows that contain the stats.
# This regex targets rows with classes that include "tw-flex tw-justify-between tw-py-3"
ROWS=$(echo "$HTML_ONELINE" | grep -oP '<tr[^>]*class="[^"]*tw-flex tw-justify-between tw-py-3[^"]*"[^>]*>.*?</tr>')

# Write CSV header
echo "Stat,Value" > "$OUTPUT_FILE"

# Process each extracted row
while IFS= read -r row; do
    # Extract the stat name from the <th> element.
    stat=$(echo "$row" | grep -oP '<th[^>]*>\s*\K[^<]+' | head -n 1 | sed 's/^[ \t]*//;s/[ \t]*$//')
    
    # Extract the stat value from the <td> element.
    value=$(echo "$row" | grep -oP '<td[^>]*>\s*(?:<span[^>]*>\s*)?\K[^<]+' | head -n 1 | sed 's/^[ \t]*//;s/[ \t]*$//')
    
    # Only output if both stat and value are non-empty.
    if [ -n "$stat" ] && [ -n "$value" ]; then
        echo "\"$stat\",\"$value\"" >> "$OUTPUT_FILE"
    fi
done <<< "$ROWS"

echo "Stats saved to $OUTPUT_FILE"

# Construct URL
URL="https://www.coingecko.com/price_charts/export/$COIN/usd.csv?from=$START_DATE&to=$END_DATE"

# Filename for the CSV
FILE_NAME="prices.csv"

# Use curl to download and save CSV
curl -L "$URL" -o "$FILE_NAME"

echo "historical data saved"