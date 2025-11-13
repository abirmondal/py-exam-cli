# Quick Start Guide

Get your exam system up and running in 15 minutes!

## For Instructors (Initial Setup)

### 1. Deploy to Vercel (5 minutes)

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

### 2. Configure Secrets (2 minutes)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add: `GRADING_SECRET` = `your-strong-secret-key`
5. Save

### 3. Enable Blob Storage (2 minutes)

1. In your project dashboard, go to **Storage**
2. Click **Create Database**
3. Select **Blob**
4. Create it (it will auto-configure)

### 4. Update URLs (5 minutes)

Edit `setup.sh`:

```bash
# Line 39 - Update your GitHub username
GITHUB_RAW_URL="https://raw.githubusercontent.com/YOUR_USERNAME/py-exam-cli/main/public/exam_files/${EXAM_CODE}.zip"

# Line 111 - Update with your Vercel URL
API_URL="https://your-project.vercel.app/api/submit"
```

Commit and push:
```bash
git add setup.sh
git commit -m "Update URLs"
git push origin main
```

### 5. Test It! (1 minute)

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
- Exam Code (e.g., `cst101`)

### 3. Complete the Exam

```bash
cd ~/exam_STU12345
ls  # See all files

# Work on your solutions
nano problem1_solution.py
nano problem2_solution.py
nano answers.txt
```

### 4. Submit

```bash
./submit.sh
```

Confirm your Enrollment ID and wait for confirmation.

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

# 6. Move to repo
mv myexam101.zip /path/to/py-exam-cli/public/exam_files/

# 7. Commit
cd /path/to/py-exam-cli
git add public/exam_files/myexam101.zip
git commit -m "Add myexam101"
git push
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
