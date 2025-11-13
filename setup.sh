#!/bin/bash

# Terminal-Based Python Exam System - Setup Script
# This script sets up the exam environment for students

set -e  # Exit on any error

echo "=== Python Exam System - Setup ==="
echo ""

# Prompt for Enrollment ID
read -p "Enter your Enrollment ID: " ENROLLMENT_ID

if [ -z "$ENROLLMENT_ID" ]; then
    echo "Error: Enrollment ID cannot be empty."
    exit 1
fi

# Prompt for Exam Code
read -p "Enter the Exam Code (e.g., cst101): " EXAM_CODE

if [ -z "$EXAM_CODE" ]; then
    echo "Error: Exam Code cannot be empty."
    exit 1
fi

echo ""
echo "Setting up exam for Enrollment ID: $ENROLLMENT_ID"
echo "Exam Code: $EXAM_CODE"
echo ""

# Create isolated exam directory
EXAM_DIR="$HOME/exam_${ENROLLMENT_ID}"

if [ -d "$EXAM_DIR" ]; then
    echo "Info: Directory $EXAM_DIR already exists. Proceeding..."
else
    echo "Creating exam directory: $EXAM_DIR"
fi

mkdir -p "$EXAM_DIR"
cd "$EXAM_DIR"

# Construct download URL for the exam zip file
# TODO: Update YOUR_USER and YOUR_REPO with your actual GitHub username and repository name
GITHUB_RAW_URL="https://raw.githubusercontent.com/abirmondal/py-exam-cli/main/public/exam_files/${EXAM_CODE}.zip"

echo "Downloading exam files..."
echo "URL: $GITHUB_RAW_URL"

# Try to download the exam zip file using curl
if command -v curl &> /dev/null; then
    curl -L -o "${EXAM_CODE}.zip" "$GITHUB_RAW_URL" -f -s -S
    DOWNLOAD_STATUS=$?
elif command -v wget &> /dev/null; then
    wget -q -O "${EXAM_CODE}.zip" "$GITHUB_RAW_URL"
    DOWNLOAD_STATUS=$?
else
    echo "Error: Neither curl nor wget is available. Please install one of them."
    exit 1
fi

# Check if the download was successful
if [ $DOWNLOAD_STATUS -ne 0 ] || [ ! -f "${EXAM_CODE}.zip" ]; then
    echo "Error: Invalid Exam Code or network issue. Please check the code and try again."
    exit 1
fi

echo "Download successful!"
echo "Extracting exam files..."

# Unzip the exam files
if command -v unzip &> /dev/null; then
    unzip -q "${EXAM_CODE}.zip"
else
    echo "Error: unzip command not found. Please install unzip."
    exit 1
fi

echo "Extraction complete!"

# Dynamically create submit.sh script
echo "Creating submission script..."

cat << 'SUBMIT_SCRIPT_EOF' > submit.sh
#!/bin/bash

# Terminal-Based Python Exam System - Submission Script
# This script submits your exam answers

set -e  # Exit on any error

echo "=== Python Exam System - Submission ==="
echo ""

# Get the enrollment ID from the parent directory name
CURRENT_DIR=$(basename "$(pwd)")
EXTRACTED_ID="${CURRENT_DIR#exam_}"

# Prompt for confirmation
read -p "Please confirm your Enrollment ID [$EXTRACTED_ID]: " CONFIRMED_ID

# Use extracted ID if user just presses Enter
if [ -z "$CONFIRMED_ID" ]; then
    CONFIRMED_ID="$EXTRACTED_ID"
fi

echo ""
echo "Preparing submission for Enrollment ID: $CONFIRMED_ID"
echo ""

# Create submission zip file name
SUBMISSION_FILE="${CONFIRMED_ID}_submission.zip"

# Remove old submission file if it exists
if [ -f "$SUBMISSION_FILE" ]; then
    rm "$SUBMISSION_FILE"
fi

# Create a list of solution files to include
# This includes common patterns for solution files
echo "Collecting solution files..."

# Create temporary list of files to zip
TEMP_FILE_LIST=$(mktemp)

# Look for solution files (customize these patterns as needed)
find . -maxdepth 1 \( -name "*solution*.py" -o -name "*solution*.txt" -o -name "answers.txt" -o -name "answer.txt" \) -type f > "$TEMP_FILE_LIST" 2>/dev/null || true

# Check if any files were found
if [ ! -s "$TEMP_FILE_LIST" ]; then
    echo "Warning: No solution files found."
    echo "Looking for: *solution*.py, *solution*.txt, answers.txt"
    rm "$TEMP_FILE_LIST"
    read -p "Do you want to continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        echo "Submission cancelled."
        exit 1
    fi
    # Create an empty zip
    touch placeholder.txt
    echo "No solution files found" > placeholder.txt
    zip -q "$SUBMISSION_FILE" placeholder.txt
    rm placeholder.txt
else
    # Create zip with only the solution files
    while IFS= read -r file; do
        echo "  Adding: $file"
    done < "$TEMP_FILE_LIST"
    
    zip -q "$SUBMISSION_FILE" $(cat "$TEMP_FILE_LIST")
fi

rm "$TEMP_FILE_LIST"

echo ""
echo "Submission package created: $SUBMISSION_FILE"
echo "Uploading submission..."
echo ""

# TODO: Update with your actual Vercel deployment URL
API_URL="https://your-vercel-deployment.vercel.app/api/submit"

# Upload using curl
if command -v curl &> /dev/null; then
    HTTP_CODE=$(curl -s -o /tmp/submit_response.txt -w "%{http_code}" -X POST -F "file=@${SUBMISSION_FILE}" "$API_URL")
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✓ Submission Successful! Your exam is submitted."
        echo ""
        cat /tmp/submit_response.txt 2>/dev/null || true
        rm -f /tmp/submit_response.txt
        exit 0
    else
        echo "✗ Submission FAILED. Please check your internet and contact your TA immediately."
        echo "Error Code: $HTTP_CODE"
        cat /tmp/submit_response.txt 2>/dev/null || true
        rm -f /tmp/submit_response.txt
        exit 1
    fi
else
    echo "Error: curl is not available. Please install curl."
    exit 1
fi
SUBMIT_SCRIPT_EOF

# Make submit.sh executable
chmod +x submit.sh

echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "You may now begin the exam."
echo "Your exam files are in: $EXAM_DIR"
echo ""
echo "When you are finished, run:"
echo "  ./submit.sh"
echo ""
echo "Good luck!"
echo ""
