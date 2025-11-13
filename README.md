# Terminal-Based Python Exam System

A complete Python & Shell-based CLI system for conducting exams. Manages setup, submission, and grading via a FastAPI backend deployed on Vercel with Blob Storage.

## 🚀 Features

- **Student Setup Script**: Download and setup exam environment with a single command
- **Automatic Submission**: Package and submit solutions via CLI
- **Serverless Backend**: FastAPI on Vercel for scalable exam management
- **Blob Storage**: Secure submission storage using Vercel Blob
- **Automated Grading**: Process multiple submissions with error resilience
- **Security**: Secret-key protected grading endpoint

## 📁 Repository Structure

```
/
├── api/
│   └── index.py              # FastAPI backend with /api/submit and /api/start-grading
├── public/
│   └── exam_files/
│       ├── cst101.zip        # Example exam (Computer Science)
│       └── phy102.zip        # Example exam (Physics)
├── setup.sh                  # Master setup script for students
├── requirements.txt          # Python dependencies for Vercel
├── vercel.json              # Vercel configuration
└── README.md                # This file
```

## 🎓 For Students

### Setup Instructions

1. **Download the setup script**:
   ```bash
   curl -O https://raw.githubusercontent.com/abirmondal/py-exam-cli/main/setup.sh
   ```

2. **Make it executable and run**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Follow the prompts**:
   - Enter your Enrollment ID (e.g., `STU12345`)
   - Enter your Full Name (e.g., `John Smith`)
   - Enter the Exam Code (e.g., `cst101`)

4. **Complete your exam**:
   - Work on the problems in the created directory
   - Edit solution files: `problem1_solution.py`, `problem2_solution.py`, etc.
   - Fill in `answers.txt` for multiple choice questions

5. **Submit your work**:
   ```bash
   ./submit.sh
   ```

### Important Notes for Students

- Work in the created `~/exam_<ENROLLMENT_ID>` directory
- DO NOT modify question files
- Only solution files will be submitted
- Ensure internet connection before submitting
- Keep your Enrollment ID handy

## 👨‍🏫 For Instructors

### Deployment to Vercel

1. **Fork or clone this repository**

2. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

3. **Login to Vercel**:
   ```bash
   vercel login
   ```

4. **Deploy the project**:
   ```bash
   vercel --prod
   ```

5. **Set up environment variables** in Vercel Dashboard:
   - Go to your project settings
   - Add environment variable: `GRADING_SECRET` (choose a strong secret key)

6. **Update the setup.sh script**:
   - Update `VERCEL_BLOB_BASE_URL` with your Vercel Blob Storage URL
   - Update the API URL in the script with your Vercel deployment URL

### Creating Exam Files

1. **Create exam content** in a temporary directory:
   ```bash
   mkdir exam_content
   cd exam_content
   
   # Create question files
   echo "Problem 1: ..." > problem1_question.txt
   
   # Create solution templates
   echo "# Solution template" > problem1_solution.py
   
   # Create answers template
   echo "Q1:\nQ2:" > answers.txt
   ```

2. **Zip the exam**:
   ```bash
   zip -r cst101.zip *.txt *.py
   ```

3. **Upload to Vercel Blob Storage**:
   - Go to your Vercel project dashboard
   - Navigate to **Storage** → **Blob**
   - Upload `cst101.zip` to the `public-exams/` folder
   - Or use Vercel CLI: `vercel blob upload cst101.zip --store public-exams`

### Starting the Grading Process

Use the `/api/start-grading` endpoint with your secret key:

```bash
curl "https://your-vercel-deployment.vercel.app/api/start-grading?secret=YOUR_SECRET_KEY"
```

This will:
- Process all submissions from Vercel Blob Storage
- Grade each submission (comparing with answer key)
- Generate a CSV file with results
- Handle corrupt files gracefully

### Downloading Results

The grading process generates `results/marks_final.csv` in Blob Storage. The response includes the URL to download this file.

## 🔧 API Endpoints

### POST `/api/submit`

Submit exam solutions.

**Request**: 
- Method: POST
- Content-Type: multipart/form-data
- Body: File upload (zip file)

**Response**:
```json
{
  "status": "success",
  "message": "Submission received successfully",
  "filename": "STU12345_submission.zip",
  "url": "https://...",
  "size": 12345
}
```

**Validations**:
- File must be ZIP format
- Maximum size: 10MB
- Must be a valid zip file

### GET `/api/start-grading`

Start automated grading process.

**Request**:
- Method: GET
- Query Parameter: `secret` (required)

**Response**:
```json
{
  "status": "Grading complete",
  "file": "results/marks_final.csv",
  "url": "https://...",
  "total_submissions": 25,
  "graded": 24,
  "errors": 1
}
```

**Security**: Requires valid `GRADING_SECRET` environment variable.

## 🔒 Security Features

1. **Secret Key Protection**: Grading endpoint secured with environment variable
2. **File Validation**: Content type and size checks
3. **Error Isolation**: Individual submission errors don't crash grading
4. **Safe Directory Operations**: No destructive `rm` commands in scripts
5. **Input Validation**: All user inputs are validated

## 🛠️ Development

### Local Testing

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the API locally**:
   ```bash
   uvicorn api.index:app --reload
   ```

3. **Test endpoints**:
   ```bash
   # Test submission
   curl -X POST -F "file=@test_submission.zip" http://localhost:8000/api/submit
   
   # Test grading (set GRADING_SECRET first)
   export GRADING_SECRET="your-secret"
   curl "http://localhost:8000/api/start-grading?secret=your-secret"
   ```

### Testing the Setup Script

```bash
# Run locally (will create exam directory in your home)
./setup.sh

# Test inputs:
# Enrollment ID: TEST123
# Exam Code: cst101
```

## 📝 Customization

### Modifying Answer Key

Edit the `ANSWERS` dictionary in `api/index.py`:

```python
ANSWERS = {
    "Q1": "A",
    "Q2": "A,C",
    "Q3": "B",
    # Add more questions
}
```

### Changing File Size Limit

Modify `MAX_FILE_SIZE` in `api/index.py`:

```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

### Solution File Patterns

Edit the patterns in the dynamically created `submit.sh` (within `setup.sh`):

```bash
find . -maxdepth 1 \( -name "*solution*.py" -o -name "answers.txt" \) -type f
```

## 🐛 Troubleshooting

### Students Cannot Download Exam

- Verify the exam code is correct
- Check that the zip file exists in `public/exam_files/`
- Ensure the GitHub raw URL is accessible
- Check internet connection

### Submission Fails

- Verify the Vercel deployment URL is correct in `submit.sh`
- Check file size (must be < 10MB)
- Ensure the zip file is valid
- Check internet connection

### Grading Fails

- Verify `GRADING_SECRET` environment variable is set
- Check Vercel Blob Storage configuration
- Ensure submissions exist in Blob Storage
- Check Vercel function logs for errors

## 📄 License

MIT License - Feel free to use and modify for your educational institution.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Important Notes

1. **Update URLs**: Before deployment, update the GitHub and Vercel URLs in `setup.sh`
2. **Set Secret**: Always set a strong `GRADING_SECRET` environment variable
3. **Test First**: Test the complete workflow before using in production
4. **Backup**: Keep backups of exam files and submissions
5. **Monitor**: Monitor Vercel function logs during exam periods
