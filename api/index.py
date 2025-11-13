"""
Terminal-Based Python Exam System - FastAPI Backend
Deployed on Vercel as a serverless function
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
import os
import io
import zipfile
import csv
import requests
from typing import Optional
from vercel_blob import put, list as blob_list, head

app = FastAPI(title="Python Exam System API")


# File size limit: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024

# Hardcoded answer key for grading
# Format: {"Question": "Answer"}
ANSWERS = {
    "Q1": "A",
    "Q2": "A,C",
    "Q3": "B",
    "Q4": "D",
    "Q5": "A,B,D"
}


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Python Exam System API",
        "version": "1.0.0",
        "endpoints": {
            "submit": "POST /api/submit",
            "start_grading": "GET /api/start-grading"
        }
    }


@app.post("/api/submit")
async def submit_exam(file: UploadFile = File(...)):
    """
    Submit exam answers.
    Accepts a zip file containing solution files.
    Saves to Vercel Blob Storage.
    """
    
    # Validate content type
    valid_content_types = [
        "application/zip",
        "application/x-zip-compressed",
        "application/octet-stream"  # Sometimes zip files come as this
    ]
    
    if file.content_type not in valid_content_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Expected ZIP file, got {file.content_type}"
        )
    
    # Validate filename
    if not file.filename or not file.filename.endswith('.zip'):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename. File must have a .zip extension"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        # Validate that it's actually a zip file
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                # Just check if we can open it
                zf.namelist()
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=400,
                detail="Invalid ZIP file. File appears to be corrupted."
            )
        
        # Upload to Vercel Blob Storage
        blob_path = f"submissions/{file.filename}"
        
        try:
            blob = put(
                pathname=blob_path,
                body=content,
                options={
                    'access': 'public',
                    'addRandomSuffix': False
                }
            )
            
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "Submission received successfully",
                    "filename": file.filename,
                    "url": blob.get('url'),
                    "size": len(content)
                }
            )
            
        except Exception as e:
            # Vercel Blob upload failed
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save submission: {str(e)}"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@app.get("/api/start-grading")
async def start_grading(secret: Optional[str] = Query(None)):
    """
    Start the grading process for all submissions.
    Secured with a secret key from environment variable.
    
    Query Parameters:
        secret: Secret key for authentication
    """
    
    # Security check: Verify secret key
    expected_secret = os.environ.get('GRADING_SECRET')
    
    if not expected_secret:
        raise HTTPException(
            status_code=500,
            detail="Grading secret not configured on server"
        )
    
    if not secret or secret != expected_secret:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid or missing secret key"
        )
    
    try:
        # List all submissions from Vercel Blob
        blobs = blob_list(options={'prefix': 'submissions/'})
        
        if not blobs or 'blobs' not in blobs:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "complete",
                    "message": "No submissions found",
                    "total_submissions": 0,
                    "graded": 0,
                    "errors": 0
                }
            )
        
        results = []
        error_count = 0
        
        # Process each submission
        for blob in blobs.get('blobs', []):
            enrollment_id = "UNKNOWN"
            student_name = "Unknown"
            start_time_utc = "N/A"
            submit_time_utc = "N/A"
            total_time_seconds = "N/A"
            
            try:
                # Extract filename
                filename = blob.get('pathname', '').split('/')[-1]
                
                # Download the blob content
                blob_url = blob.get('url')
                if not blob_url:
                    raise Exception("Blob URL not found")
                
                # Download blob content from URL
                response = requests.get(blob_url, timeout=30)
                response.raise_for_status()
                blob_data = response.content
                
                # Open as ZipFile
                with zipfile.ZipFile(io.BytesIO(blob_data)) as zf:
                    # Try to read student_info.txt
                    try:
                        with zf.open('student_info.txt') as info_file:
                            info_content = info_file.read().decode('utf-8')
                            # Parse the file
                            for line in info_content.strip().split('\n'):
                                if line.startswith('ENROLLMENT_ID:'):
                                    enrollment_id = line.split(':', 1)[1].strip()
                                elif line.startswith('STUDENT_NAME:'):
                                    student_name = line.split(':', 1)[1].strip()
                                elif line.startswith('START_TIME_UTC:'):
                                    start_time_utc = line.split(':', 1)[1].strip()
                                elif line.startswith('SUBMIT_TIME_UTC:'):
                                    submit_time_utc = line.split(':', 1)[1].strip()
                                elif line.startswith('TOTAL_TIME_SECONDS:'):
                                    total_time_seconds = line.split(':', 1)[1].strip()
                    except KeyError:
                        # student_info.txt not found, fallback to filename
                        if filename.endswith('_submission.zip'):
                            enrollment_id = filename.replace('_submission.zip', '')
                        else:
                            enrollment_id = filename.replace('.zip', '')
                        student_name = "Unknown"
                    
                    # Read and grade answers.txt
                    score = 0
                    total_questions = len(ANSWERS)
                    
                    try:
                        with zf.open('answers.txt') as answer_file:
                            answer_content = answer_file.read().decode('utf-8')
                            
                            # Parse answers
                            student_answers = {}
                            for line in answer_content.strip().split('\n'):
                                line = line.strip()
                                # Skip comments and empty lines
                                if not line or line.startswith('#'):
                                    continue
                                # Parse format: Q1: A or Q2: A,C
                                if ':' in line:
                                    parts = line.split(':', 1)
                                    question = parts[0].strip()
                                    answer = parts[1].strip()
                                    if answer:  # Only add if answer is not empty
                                        student_answers[question] = answer
                            
                            # Calculate score by comparing with ANSWERS
                            for question, correct_answer in ANSWERS.items():
                                if question in student_answers:
                                    if student_answers[question] == correct_answer:
                                        score += 1
                            
                    except KeyError:
                        # answers.txt not found
                        raise Exception("answers.txt not found in submission")
                
                results.append({
                    "enrollment_id": enrollment_id,
                    "student_name": student_name,
                    "score": score,
                    "status": "Graded",
                    "filename": filename,
                    "start_time_utc": start_time_utc,
                    "submit_time_utc": submit_time_utc,
                    "total_time_seconds": total_time_seconds
                })
                
            except Exception as e:
                # Handle errors for individual submissions
                error_count += 1
                results.append({
                    "enrollment_id": enrollment_id,
                    "student_name": student_name,
                    "score": 0,
                    "status": f"Error: {str(e)[:50]}",
                    "filename": blob.get('pathname', 'unknown'),
                    "start_time_utc": start_time_utc,
                    "submit_time_utc": submit_time_utc,
                    "total_time_seconds": total_time_seconds
                })
        
        # Convert results to CSV
        csv_buffer = io.StringIO()
        if results:
            fieldnames = ["enrollment_id", "student_name", "score", "status", "filename", 
                         "start_time_utc", "submit_time_utc", "total_time_seconds"]
            writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        csv_content = csv_buffer.getvalue()
        
        # Save CSV to Vercel Blob
        result_blob = put(
            pathname='results/marks_final.csv',
            body=csv_content.encode('utf-8'),
            options={
                'access': 'public',
                'addRandomSuffix': False
            }
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "Grading complete",
                "file": "results/marks_final.csv",
                "url": result_blob.get('url'),
                "total_submissions": len(results),
                "graded": len(results) - error_count,
                "errors": error_count
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Grading process failed: {str(e)}"
        )


# Vercel requires a handler for the serverless function
handler = app
