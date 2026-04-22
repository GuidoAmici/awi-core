#!/bin/bash
# /home/csr1/bounty-bot/.gemini/key_manager.sh
# This script attempts to set an active GEMINI_API_KEY from a list.

# --- Configuration ---
# Path to the file containing the API keys array
API_KEYS_FILE="$HOME/bounty-bot/.gemini/api_keys.sh" 
# Environment variable that gemini CLI uses for API key.
# Adjust if gemini CLI uses a different variable name (e.g., GOOGLE_API_KEY).
ENV_VAR_NAME="GEMINI_API_KEY" 
# A simple, fast, low-cost gemini command to test the key.
TEST_COMMAND="gemini --version" 
# --- End Configuration ---

# Ensure the API keys file exists
if [ ! -f "$API_KEYS_FILE" ]; then
    echo "Error: API keys file not found at $API_KEYS_FILE. Please create it."
    exit 1
fi

# Source the API keys file to load the GEMINI_API_KEYS array
# '|| true' prevents script exit if sourcing fails, allowing subsequent checks
source "$API_KEYS_FILE" || echo "Warning: Could not source $API_KEYS_FILE."

# Check if the GEMINI_API_KEYS array was loaded and is not empty
if [ -z "$GEMINI_API_KEYS" ]; then
    echo "Error: GEMINI_API_KEYS array is empty or not loaded from $API_KEYS_FILE. Please check the file content."
    exit 1
fi

# Function to test a key and return success status (0 for success, 1 for failure)
test_key() {
    local api_key="$1"
    # Set the environment variable for the current key
    export "$ENV_VAR_NAME"="$api_key"
    echo "Attempting to use Gemini API key ending in ***${api_key: -4}..."

    # Execute the test command and capture output/exit code
    # Suppress normal output, only show errors indicating failure.
    if eval "$TEST_COMMAND" > /dev/null 2>&1; then
        echo "Success: API key confirmed active."
        return 0 # Success
    else
        echo "Failed: Key may be invalid or quota exhausted."
        unset "$ENV_VAR_NAME" # Unset the variable if it failed for a clean state
        return 1 # Failure
    fi
}

# Loop through the keys
ACTIVE_KEY_FOUND=false
for key in "${GEMINI_API_KEYS[@]}"; do
    if test_key "$key"; then
        ACTIVE_KEY_FOUND=true
        echo "Active Gemini API key set successfully in environment variable '$ENV_VAR_NAME'."
        break # Exit loop once a working key is found
    fi
done

if [ "$ACTIVE_KEY_FOUND" = false ]; then
    echo "Error: All provided Gemini API keys failed. Please check your keys and quotas."
    exit 1
fi
