# Deployment Guide

This guide will help you deploy the Terminal-Based Python Exam System to Vercel.

## Prerequisites

- A GitHub account
- A Vercel account (free tier works fine)
- Git installed locally
- Node.js and npm installed (for Vercel CLI)

## New Features in Latest Update

This system now includes enhanced features:

- **Student Identification**: Collects both Enrollment ID and Full Name for better tracking
- **Vercel Blob Hosting**: Exam files are hosted on Vercel Blob Storage (no GitHub files needed)
- **Real Grading**: Actual implementation that downloads, parses, and grades submissions
- **Enhanced CSV Output**: Results include enrollment_id, student_name, score, status, and filename
- **Student Info File**: `student_info.txt` is automatically created and included in submissions

## Step-by-Step Deployment

### Method 1: GitHub Integration (Recommended)

This is the easiest and most maintainable approach.

#### 1. Fork or Push to GitHub

```bash
# Fork this repository on GitHub, or push to your own repo
git clone https://github.com/abirmondal/py-exam-cli.git
cd py-exam-cli

# If creating your own repo:
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

#### 2. Import to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New... > Project**
3. Click **Import** next to your GitHub repository
4. Vercel will detect the configuration automatically

#### 3. Configure Environment Variables

Before clicking Deploy:

1. Expand the **Environment Variables** section
2. Add a new variable:
   - **Name**: `GRADING_SECRET`
   - **Value**: Choose a strong, random secret (e.g., a UUID)
   - **Environment**: Select all (Production, Preview, Development)
3. Click **Deploy**

#### 4. Set Up Blob Storage

After deployment completes:

1. In your Vercel project dashboard, go to **Storage** tab
2. Click **Create Database**
3. Select **Blob**
4. Choose a name (e.g., "exam-storage")
5. Click **Create**

Vercel will automatically configure the `BLOB_READ_WRITE_TOKEN` environment variable.

#### 5. Get Your Blob Storage URL

In the Storage section, you'll see your Blob Storage URL:
```
https://[your-project-id].blob.vercel-storage.com
```

#### 6. Update setup.sh

Update the URLs in `setup.sh`:

```bash
# Around line 63:
VERCEL_BLOB_BASE_URL="https://your-actual-blob-url.blob.vercel-storage.com"

# Around line 241 (in submit.sh):
API_URL="https://your-project.vercel.app/api/submit"
```

Commit and push to GitHub:
```bash
git add setup.sh
git commit -m "Update deployment URLs"
git push origin main
```

Vercel will automatically detect the push and redeploy!

#### 7. Future Updates

Just commit and push to your main branch:
```bash
git add .
git commit -m "Your changes"
git push origin main
```

Vercel automatically redeploys on every push.

---

### Method 2: Vercel CLI (Advanced)

For users who prefer command-line deployment.

#### 1. Fork or Clone the Repository

```bash
git clone https://github.com/abirmondal/py-exam-cli.git
cd py-exam-cli
```

#### 2. Customize URLs

Open `setup.sh` and update the Vercel Blob URL (around line 63):

```bash
# Change this line:
VERCEL_BLOB_BASE_URL="https://[YOUR-VERCEL-PROJECT-ID].blob.vercel-storage.com"

# To your actual Vercel Blob Storage URL:
VERCEL_BLOB_BASE_URL="https://your-actual-blob-url.blob.vercel-storage.com"
```

You can find your Vercel Blob Storage URL in your Vercel project's Storage settings.

#### 3. Install Vercel CLI

```bash
npm install -g vercel
```

#### 4. Login to Vercel

```bash
vercel login
```

Follow the prompts to authenticate with your Vercel account.

#### 5. Deploy the Project

```bash
# Deploy to production
vercel --prod
```

The CLI will guide you through:
- Linking to an existing project or creating a new one
- Configuring project settings
- Deploying the application

### 6. Configure Environment Variables

After deployment, you need to set up the `GRADING_SECRET` environment variable:

1. Go to your Vercel dashboard: https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add a new environment variable:
   - **Name**: `GRADING_SECRET`
   - **Value**: Choose a strong, random secret (e.g., a UUID or long random string)
   - **Environment**: Select all (Production, Preview, Development)
5. Click **Save**

### 7. Configure Vercel Blob Storage

The system uses Vercel Blob Storage for:
- Hosting exam files (in `public-exams/` path)
- Storing student submissions (in `submissions/` path)
- Storing grading results (in `results/` path)

**Setup Steps:**

1. In your Vercel project dashboard, go to **Storage**
2. Click **Create Database**
3. Select **Blob**
4. Choose a name for your store (e.g., "exam-submissions")
5. Click **Create**

Vercel will automatically configure the necessary environment variables for Blob Storage (`BLOB_READ_WRITE_TOKEN`).

**Get Your Blob Storage URL:**

After creating Blob Storage, you'll receive a URL like:
```
https://[your-project-id].blob.vercel-storage.com
```

Save this URL - you'll need it for updating `setup.sh` in the next step.

### 8. Update API URL in setup.sh

After deployment, Vercel will give you a URL (e.g., `https://your-project.vercel.app`).

You need to update the API URL in the `setup.sh` file that gets dynamically created.

Edit `setup.sh` around line 162 (within the submit.sh HEREDOC) and change:

```bash
API_URL="https://your-vercel-deployment.vercel.app/api/submit"
```

To your actual Vercel URL:

```bash
API_URL="https://your-project-name.vercel.app/api/submit"
```

### 9. Commit and Push Changes

```bash
git add setup.sh
git commit -m "Update URLs for deployment"
git push origin main
```

### 10. Redeploy (if needed)

If you made changes after the initial deployment:

```bash
vercel --prod
```

## Verify Deployment

### Test the API

1. Visit your Vercel URL in a browser: `https://your-project.vercel.app`
2. You should see a JSON response with API information

### Test Submission Endpoint

```bash
# Create a test zip file
cd /tmp
echo "Test content" > test.txt
zip test.zip test.txt

# Test the submission
curl -X POST -F "file=@test.zip" https://your-project.vercel.app/api/submit
```

You should get a success response.

### Test Grading Endpoint

```bash
curl "https://your-project.vercel.app/api/start-grading?secret=YOUR_SECRET_KEY"
```

Replace `YOUR_SECRET_KEY` with the value you set in environment variables.

## Add Exam Files

### 1. Create Your Exam Content

```bash
mkdir exam_content
cd exam_content

# Create your exam files
echo "Question 1..." > problem1_question.txt
echo "# Solution template" > problem1_solution.py
echo "Q1:\nQ2:" > answers.txt
```

### 2. Create the Zip File

```bash
zip -r myexam101.zip *.txt *.py
```

### 3. Upload to Vercel Blob Storage

You have two options to upload exam files:

**Option 1: Via Vercel Dashboard**
1. Go to your Vercel project dashboard
2. Navigate to **Storage** → **Blob**
3. Create a folder path: `public-exams/`
4. Upload `myexam101.zip` to this folder

**Option 2: Via Vercel CLI**
```bash
# Install Vercel CLI if not already installed
npm install -g vercel

# Upload the exam file
vercel blob upload myexam101.zip --token YOUR_TOKEN

# Or upload to a specific path
# (Note: Exact CLI syntax may vary, check Vercel docs)
```

The exam will be immediately available at:
```
https://your-blob-url.blob.vercel-storage.com/public-exams/myexam101.zip
```

## Student Instructions

### Distribute to Students

1. **Setup Script URL**:
   ```
   https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/setup.sh
   ```

2. **Instructions for Students**:
   ```
   1. Download setup script:
      curl -O https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/setup.sh
   
   2. Make it executable:
      chmod +x setup.sh
   
   3. Run setup:
      ./setup.sh
   
   4. Enter your Enrollment ID when prompted
   5. Enter your Full Name when prompted
   6. Enter the Exam Code (e.g., cst101)
   7. Navigate to the exam directory:
      cd ~/exam_YOUR_ENROLLMENT_ID
   
   8. Start the exam (starts timer and unlocks solution files):
      ./start_exam.sh
   
   9. Complete the exam (edit solution files)
   
   10. Submit (locks files and submits):
       ./submit.sh
   ```

**Important Notes**:
- Files are read-only until `start_exam.sh` is run
- Time is tracked from start to submission
- Both Enrollment ID and Full Name are collected
- `student_info.txt` includes timing data for auditing

## Monitoring and Maintenance

### View Logs

1. Go to your Vercel dashboard
2. Select your project
3. Go to **Deployments**
4. Click on a deployment
5. View **Functions** logs

### Download Submissions

After students submit, you can:

1. Use the grading endpoint to process all submissions
2. Download the results CSV from Vercel Blob Storage
3. Or manually access Blob Storage through the Vercel dashboard

### Grading Process

```bash
# Start grading with your secret
curl "https://your-project.vercel.app/api/start-grading?secret=YOUR_SECRET"
```

This will:
- Download all submissions from Vercel Blob Storage
- Read student information from `student_info.txt` in each submission
- Parse and compare answers with the answer key
- Calculate real scores based on correct answers
- Generate a CSV file with results including:
  - `enrollment_id`: Student's enrollment ID
  - `student_name`: Student's full name
  - `score`: Calculated score
  - `status`: Grading status or error message
  - `filename`: Original submission filename
  - `start_time_utc`: When student started the exam
  - `submit_time_utc`: When student submitted
  - `total_time_seconds`: Total time taken in seconds
- Return the URL to download the CSV from Blob Storage

## Troubleshooting

### Deployment Fails

**Error**: "No build matches your repository"
- **Solution**: Make sure `vercel.json` is in the repository root

**Error**: "Failed to install dependencies"
- **Solution**: Check that `requirements.txt` is valid
- Try: `pip install -r requirements.txt` locally first
- Ensure all dependencies are available: fastapi, uvicorn, python-multipart, vercel-blob, requests

### API Errors

**Error**: "Grading secret not configured"
- **Solution**: Set the `GRADING_SECRET` environment variable in Vercel

**Error**: "Failed to save submission"
- **Solution**: Ensure Vercel Blob Storage is configured
- Check that the BLOB_READ_WRITE_TOKEN is set (automatic with Blob)

### Students Can't Download Exams

**Error**: "Invalid Exam Code or network issue"
- **Solution**: 
  1. Verify the exam zip file exists in Vercel Blob Storage under `public-exams/`
  2. Check the `VERCEL_BLOB_BASE_URL` in `setup.sh` is correct
  3. Ensure the blob is accessible (public access enabled)
  4. Test the URL in a browser: `https://your-blob-url.blob.vercel-storage.com/public-exams/examcode.zip`
  5. Check Vercel Blob Storage logs in the dashboard

### Submissions Fail

**Error**: "Submission FAILED"
- **Solution**:
  1. Check the Vercel deployment URL is correct in `setup.sh`
  2. Verify the API endpoint is working
  3. Check file size (must be < 10MB)
  4. Test with: `curl -X POST -F "file=@submission.zip" https://your-url/api/submit`

## Security Best Practices

1. **Protect Your Secret Key**
   - Never commit the `GRADING_SECRET` to the repository
   - Use a strong, random value
   - Rotate it periodically

2. **Monitor Access**
   - Review Vercel function logs regularly
   - Watch for suspicious activity
   - Set up alerts in Vercel dashboard

3. **Backup Data**
   - Regularly download submissions from Blob Storage
   - Keep local backups of exam files
   - Export grading results frequently

4. **Access Control**
   - Only share the grading endpoint with authorized personnel
   - Keep the secret key confidential
   - Use different secrets for different exam periods

## Cost Considerations

### Vercel Free Tier Limits

- **Function Invocations**: 100,000/month
- **Function Duration**: 100 GB-hours/month
- **Bandwidth**: 100 GB/month
- **Blob Storage**: 1 GB free

For a typical exam with 100 students:
- Setup downloads: ~0.5 MB × 100 = 50 MB
- Submissions: ~1 MB × 100 = 100 MB
- Total: ~150 MB (well within limits)

### Upgrading

If you need more resources:
- Vercel Pro: $20/month
- Includes 1000 GB bandwidth
- Custom domains
- Better support

## Updates and Maintenance

### Update Exam System

```bash
# Pull latest changes
git pull origin main

# Deploy
vercel --prod
```

### Add New Features

1. Make changes locally
2. Test thoroughly
3. Commit and push
4. Deploy to Vercel

## Support

For issues or questions:
- Check the README.md
- Review Vercel documentation: https://vercel.com/docs
- Check function logs in Vercel dashboard
- Review error messages carefully

## Advanced Configuration

### Custom Domain

1. In Vercel dashboard, go to **Settings** → **Domains**
2. Add your custom domain
3. Configure DNS according to Vercel instructions
4. Update the API URL in `setup.sh`

### Function Timeout

If grading takes too long, increase the timeout in `vercel.json`:

```json
{
  "functions": {
    "api/index.py": {
      "maxDuration": 60
    }
  }
}
```

### CORS Configuration

If you need to access the API from a web interface, add CORS middleware in `api/index.py`.

## System Workflow Summary

### For Students:
1. Download and run `setup.sh`
2. Provide Enrollment ID and Full Name
3. Enter Exam Code
4. System downloads exam from Vercel Blob Storage
5. System creates `student_info.txt` with ID and name
6. All files set to read-only for integrity
7. Run `start_exam.sh` to begin (starts timer, unlocks solution files)
8. Complete exam in isolated directory
9. Run `submit.sh` to upload (locks files, records end time, includes all timing data)

### For Instructors:
1. Create exam zip files
2. Upload to Vercel Blob Storage under `public-exams/`
3. Students take exam and submit
4. Call `/api/start-grading` endpoint
5. System downloads all submissions from Blob
6. System reads student info (including timing data) and grades answers
7. System generates CSV with enrollment_id, student_name, score, status, timing info
8. Download results from returned URL with complete audit trail

## Conclusion

Your Terminal-Based Python Exam System is now deployed and ready to use! Students can download the setup script, take exams, and submit their work. You can process submissions and generate grades with a single API call.

For production use, make sure to:
- ✓ Set strong secret keys
- ✓ Update Vercel Blob URL in setup.sh
- ✓ Upload exam files to Vercel Blob Storage (not GitHub)
- ✓ Test the complete workflow: setup → start_exam → submit
- ✓ Verify timing data is captured correctly
- ✓ Monitor during exam periods
- ✓ Keep backups of all data
- ✓ Review logs and timing anomalies regularly
