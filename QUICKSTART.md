# Quick Start Guide

Get your exam system up and running in 15 minutes!

## For Instructors (Initial Setup)

### Method 1: GitHub Integration (Recommended - 10 minutes)

1. **Fork this repository** to your GitHub account

2. **Go to Vercel Dashboard** and click **Add New... > Project**

3. **Import your GitHub repository**

4. **Add Environment Variable**:
   - Before deploying, expand "Environment Variables"
   - Add `GRADING_SECRET` = `your-strong-secret-key`
   - Click **Deploy**

5. **Set up Blob Storage**:
   - Go to **Storage** tab → **Create Database** → **Blob**
   - Vercel auto-configures the required environment variables

6. **Update URLs in setup.sh** (commit to GitHub):
   - Update `VERCEL_BLOB_BASE_URL` with your Blob Storage URL
   - Update `API_URL` with your Vercel deployment URL
   - Vercel will auto-redeploy when you push

### Method 2: Vercel CLI (Advanced - 10 minutes)

```bash
# Install Vercel CLI
npm install -g vercel

# Clone this repository
git clone https://github.com/abirmondal/py-exam-cli.git
cd py-exam-cli

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

Then configure as above:
1. Add `GRADING_SECRET` environment variable in Vercel Dashboard
2. Create Blob Storage in Storage tab
3. Update URLs in setup.sh

### Test It! (1 minute)

```bash
# Test the API
curl https://your-project.vercel.app/

# Should return: {"message": "Python Exam System API", ...}
```

**Done!** Your exam system is live! 🎉

---

## For Students (Taking an Exam)

### 1. Download Setup Script

```bash
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/py-exam-cli/main/setup.sh
```

### 2. Run Setup

```bash
chmod +x setup.sh
./setup.sh
```

Enter:
- Your Enrollment ID (e.g., `STU12345`)
- Your Full Name (e.g., `John Smith`)
- Exam Code (e.g., `cst101`)

### 3. Start the Exam

```bash
cd ~/exam_STU12345
./start_exam.sh
```

This starts the timer and makes solution files editable.

### 4. Complete the Exam

```bash
# Work on your solutions
nano problem1_solution.py
nano problem2_solution.py
nano answers.txt
```

### 5. Submit

```bash
./submit.sh
```

This locks files and submits. Confirm your Enrollment ID and wait for confirmation.

**Done!** Your exam is submitted! ✓

---

## For Instructors (Creating Exams)

### Quick Exam Creation

```bash
# 1. Create a directory
mkdir my_exam
cd my_exam

# 2. Create question files
cat > problem1_question.txt << 'EOF'
Problem 1: Write a function to add two numbers
EOF

# 3. Create solution templates
cat > problem1_solution.py << 'EOF'
def add(a, b):
    # Your code here
    pass
EOF

# 4. Create answers template
cat > answers.txt << 'EOF'
Q1: 
Q2: 
EOF

# 5. Create the zip
zip -r myexam101.zip *.txt *.py

# 6. Upload to Vercel Blob Storage
# Option 1: Via Vercel Dashboard
# - Go to your project → Storage → Blob
# - Upload myexam101.zip to public-exams/ folder

# Option 2: Via Vercel CLI
vercel blob upload myexam101.zip --store public-exams
```

**Done!** Your exam is available! Students can now use exam code `myexam101`.

---

## For Instructors (Grading)

### Start Grading Process

```bash
curl "https://your-project.vercel.app/api/start-grading?secret=YOUR_SECRET"
```

Response:
```json
{
  "status": "Grading complete",
  "file": "results/marks_final.csv",
  "url": "https://blob.vercel-storage.com/.../marks_final.csv",
  "total_submissions": 25,
  "graded": 24,
  "errors": 1
}
```

### Download Results

Click the URL in the response to download the CSV file with grades.

**Done!** All submissions graded! 📊

---

## Common Commands

### Update Answer Key

Edit `api/index.py`:
```python
ANSWERS = {
    "Q1": "A",
    "Q2": "A,C",
    "Q3": "B",
    # Add more...
}
```

### Re-deploy After Changes

```bash
git add .
git commit -m "Update answer key"
git push
vercel --prod
```

### View Logs

```bash
vercel logs
```

### Test Submission Locally

```bash
# Create a test zip
echo "Q1: A" > answers.txt
zip test.zip answers.txt

# Submit it
curl -X POST -F "file=@test.zip" https://your-project.vercel.app/api/submit
```

---

## Troubleshooting

### "Invalid Exam Code" Error
- ✓ Check the zip file exists in `public/exam_files/`
- ✓ Verify the exam code matches the filename (without .zip)
- ✓ Ensure the repository is public

### "Submission FAILED" Error
- ✓ Check the Vercel URL is correct in `setup.sh`
- ✓ Verify Blob Storage is configured
- ✓ Test the API: `curl https://your-url.vercel.app/`

### "Grading secret not configured"
- ✓ Set `GRADING_SECRET` in Vercel environment variables
- ✓ Redeploy after adding environment variables

---

## Support

- 📖 Read the full [README.md](README.md)
- 🚀 See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment
- 🤝 Check [CONTRIBUTING.md](CONTRIBUTING.md) for customization

---

## Next Steps

1. ✓ Create your first exam
2. ✓ Test with a friend
3. ✓ Share the setup script with students
4. ✓ Monitor submissions in Vercel dashboard
5. ✓ Run grading after exam deadline

**Happy Examining!** 🎓
