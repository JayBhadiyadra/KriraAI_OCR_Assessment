# GitHub Upload Guide

Follow these steps to upload your project to GitHub and share it with the company.

## Prerequisites

### Step 1: Install Git (if not already installed)

1. Download Git for Windows from: https://git-scm.com/download/win
2. Run the installer with default settings
3. Restart your terminal/command prompt after installation

### Step 2: Verify Git Installation

Open a new command prompt and run:
```bash
git --version
```

You should see something like: `git version 2.x.x`

---

## Upload to GitHub

### Step 3: Create a GitHub Account (if you don't have one)

1. Go to https://github.com
2. Sign up for a free account
3. Verify your email address

### Step 4: Create a New Repository on GitHub

1. Log in to GitHub
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `KriraAI_OCR_Assessment` (or any name you prefer)
   - **Description**: "OCR-based text extraction system for shipping labels"
   - **Visibility**: Choose **Public** (so company can access) or **Private** (if you prefer)
   - **DO NOT** check "Initialize with README" (we already have one)
   - **DO NOT** add .gitignore or license (we already have .gitignore)
5. Click **"Create repository"**

### Step 5: Initialize Git in Your Project Folder

Open Command Prompt in your project directory and run:

```bash
cd E:\KriraAI_Assessment

# Initialize git repository
git init

# Add all files (except those in .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: OCR text extraction system for waybill images"
```

### Step 6: Connect to GitHub and Push

After creating the repository on GitHub, you'll see a page with setup instructions. Use these commands:

```bash
# Add GitHub repository as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**Note**: You'll be prompted for your GitHub username and password. For password, use a **Personal Access Token** (see Step 7 below).

### Step 7: Create Personal Access Token (for authentication)

Since GitHub no longer accepts passwords, you need a Personal Access Token:

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click **"Generate new token (classic)"**
3. Give it a name: "OCR Assessment Upload"
4. Select scopes: Check **"repo"** (full control of private repositories)
5. Click **"Generate token"**
6. **Copy the token immediately** (you won't see it again!)
7. When prompted for password during `git push`, paste this token instead

---

## Alternative: Using GitHub Desktop (Easier Method)

If you prefer a graphical interface:

1. Download GitHub Desktop: https://desktop.github.com/
2. Install and sign in with your GitHub account
3. Click **"File" → "Add Local Repository"**
4. Browse to `E:\KriraAI_Assessment`
5. Click **"Publish repository"**
6. Choose visibility (Public/Private)
7. Click **"Publish repository"**

---

## Verify Upload

1. Go to your GitHub repository page
2. You should see all your files:
   - README.md
   - requirements.txt
   - app.py
   - process_dataset.py
   - src/ folder
   - etc.

3. Check that:
   - ✅ README.md is visible and formatted correctly
   - ✅ All source code files are present
   - ✅ .gitignore is working (venv folder should NOT be visible)
   - ✅ results/ folder is visible (if you want to include it)

---

## Share Repository Link

Once uploaded, copy the repository URL from your browser:
```
https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
```

Share this link with the company for assessment.

---

## Optional: Add Repository Description and Topics

1. Go to your repository on GitHub
2. Click the **"⚙️ Settings"** icon (gear icon) next to "About"
3. Add description: "OCR-based text extraction system for shipping label images"
4. Add topics: `ocr`, `python`, `streamlit`, `easyocr`, `image-processing`, `text-extraction`

---

## Troubleshooting

### Issue: "git: command not found"
- **Solution**: Install Git (Step 1) and restart your terminal

### Issue: "Authentication failed" during push
- **Solution**: Use Personal Access Token instead of password (Step 7)

### Issue: "remote origin already exists"
- **Solution**: Remove and re-add:
  ```bash
  git remote remove origin
  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
  ```

### Issue: "failed to push some refs"
- **Solution**: Pull first, then push:
  ```bash
  git pull origin main --allow-unrelated-histories
  git push -u origin main
  ```

### Issue: Want to exclude results folder
- **Solution**: Edit `.gitignore` and uncomment the `results/` lines

---

## Quick Command Reference

```bash
# Check status
git status

# Add all changes
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push origin main

# View commit history
git log --oneline
```

---

Good luck with your assessment! 🚀


