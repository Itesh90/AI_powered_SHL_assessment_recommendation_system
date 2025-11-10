# Deployment Guide - SHL Assessment Recommendation System

This guide covers deploying both the backend API and frontend to production.

## 📋 Prerequisites

- GitHub account
- Render/Railway/Heroku account (for backend)
- Vercel account (for frontend) - Already set up!
- Git installed on your machine

---

## Step 1: Push Code to GitHub

### 1.1 Initialize Git Repository (if not already done)

```powershell
# Navigate to your project directory
cd "E:\Sales Force Gen AI\AI_powered_SHL_assessment_recommendation_system"

# Initialize git (if not already initialized)
git init

# Check current status
git status
```

### 1.2 Create .gitignore File (if not exists)

```powershell
# Create .gitignore if it doesn't exist
if (!(Test-Path .gitignore)) {
    @"
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
.venv/
venv/
env/
ENV/
*.log
.DS_Store
.env
.vercel/
"@ | Out-File -FilePath .gitignore -Encoding utf8
}
```

### 1.3 Add and Commit Files

```powershell
# Add all files
git add .

# Commit with a message
git commit -m "Initial commit: SHL Assessment Recommendation System"

# Check if remote exists
git remote -v
```

### 1.4 Create GitHub Repository and Push

**Option A: Create via GitHub Website**
1. Go to https://github.com/new
2. Repository name: `AI_powered_SHL_assessment_recommendation_system`
3. Set to Public or Private
4. Click "Create repository"
5. Copy the repository URL (e.g., `https://github.com/yourusername/AI_powered_SHL_assessment_recommendation_system.git`)

**Option B: Use GitHub CLI (if installed)**
```powershell
gh repo create AI_powered_SHL_assessment_recommendation_system --public --source=. --remote=origin --push
```

**Then push your code:**
```powershell
# Add remote (replace with your GitHub username)
git remote add origin https://github.com/yourusername/AI_powered_SHL_assessment_recommendation_system.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Backend API

### Option A: Deploy to Render (Recommended - Free Tier Available)

#### 2.1 Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (recommended for easy integration)

#### 2.2 Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select your repository: `AI_powered_SHL_assessment_recommendation_system`

#### 2.3 Configure Service Settings
- **Name**: `shl-assessment-api` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave empty (or `./` if needed)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`
- **Environment Variables**:
  - `PORT`: `8000` (Render sets this automatically, but good to have)
  - `OPENAI_API_KEY`: `your-openai-api-key-here` (optional, but recommended)

#### 2.4 Deploy
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Your API will be available at: `https://your-service-name.onrender.com`

#### 2.5 Get Your API URL
- Copy the service URL from Render dashboard
- Example: `https://shl-assessment-api.onrender.com`

---

### Option B: Deploy to Railway

#### 2.1 Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub

#### 2.2 Deploy Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway auto-detects Python and installs dependencies

#### 2.3 Configure Environment Variables
1. Go to "Variables" tab
2. Add:
   - `PORT`: `8000` (Railway sets this automatically)
   - `OPENAI_API_KEY`: `your-openai-api-key-here`

#### 2.4 Get Your API URL
- Railway provides a URL like: `https://your-project.up.railway.app`

---

### Option C: Deploy to Heroku

#### 2.1 Install Heroku CLI
```powershell
# Download from https://devcenter.heroku.com/articles/heroku-cli
# Or use winget
winget install Heroku.HerokuCLI
```

#### 2.2 Login and Create App
```powershell
heroku login
heroku create shl-assessment-api
```

#### 2.3 Set Environment Variables
```powershell
heroku config:set OPENAI_API_KEY=your-openai-api-key-here
heroku config:set PORT=8000
```

#### 2.4 Deploy
```powershell
git push heroku main
```

#### 2.5 Get Your API URL
```powershell
heroku info
# Your app will be at: https://shl-assessment-api.herokuapp.com
```

---

## Step 3: Deploy Frontend

### Option A: Deploy to Vercel (Recommended - Already Configured!)

#### 3.1 Connect GitHub Repository
1. Go to https://vercel.com
2. Click "Add New Project"
3. Import your GitHub repository
4. Select: `AI_powered_SHL_assessment_recommendation_system`

#### 3.2 Configure Project Settings
- **Framework Preset**: Other (or leave as auto-detected)
- **Root Directory**: `./` (root)
- **Build Command**: Leave empty (Vercel will auto-detect)
- **Output Directory**: Leave empty
- **Install Command**: Leave empty

#### 3.3 Environment Variables (Optional)
- `OPENAI_API_KEY`: `your-openai-api-key-here` (if you want to use OpenAI)

#### 3.4 Deploy
1. Click "Deploy"
2. Wait for build to complete (2-5 minutes)
3. Your frontend will be at: `https://your-project-name.vercel.app`

#### 3.5 Update Frontend API URL
After deployment, update `index.html` with your backend API URL:

```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'https://your-backend-api.onrender.com'; // Your Render/Railway/Heroku URL
```

Then commit and push:
```powershell
git add index.html
git commit -m "Update API URL for production"
git push
```

Vercel will automatically redeploy.

---

### Option B: Deploy to Netlify

#### 3.1 Create Netlify Account
1. Go to https://netlify.com
2. Sign up with GitHub

#### 3.2 Deploy Site
1. Click "Add new site" → "Import an existing project"
2. Connect to GitHub
3. Select your repository
4. Build settings:
   - **Build command**: Leave empty
   - **Publish directory**: `./` (or leave empty)

#### 3.3 Deploy
1. Click "Deploy site"
2. Your site will be at: `https://random-name.netlify.app`
3. You can change the name in Site settings

---

### Option C: Deploy to GitHub Pages

#### 3.1 Enable GitHub Pages
1. Go to your GitHub repository
2. Settings → Pages
3. Source: Deploy from a branch
4. Branch: `main` / `root`
5. Click "Save"

#### 3.2 Access Your Site
- Your site will be at: `https://yourusername.github.io/AI_powered_SHL_assessment_recommendation_system/`

**Note**: GitHub Pages only serves static files. You'll need to update `index.html` to point to your deployed backend API.

---

## Step 4: Update Frontend to Use Backend API

After deploying both frontend and backend, update the API URL in `index.html`:

```powershell
# Edit index.html and update the API_BASE_URL
# Replace the Render/Railway/Heroku URL with your actual backend URL
```

Example:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'https://shl-assessment-api.onrender.com'; // Your actual backend URL
```

Then commit and push:
```powershell
git add index.html
git commit -m "Update API URL for production deployment"
git push
```

---

## Step 5: Test from Deployed URLs

### 5.1 Test Backend API

**Health Check:**
```powershell
# Replace with your actual backend URL
Invoke-RestMethod -Uri "https://your-backend-api.onrender.com/health" -Method Get
```

**Get Recommendations:**
```powershell
$body = @{
    query = "Java developer with problem-solving skills"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://your-backend-api.onrender.com/recommend" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

**API Documentation:**
- Visit: `https://your-backend-api.onrender.com/docs`
- Interactive Swagger UI should be available

### 5.2 Test Frontend

1. Visit your frontend URL (e.g., `https://your-project.vercel.app`)
2. Enter a test query: "Java developer with communication skills"
3. Click "Get Recommendations"
4. Verify results are displayed

### 5.3 Test API Endpoints from Frontend

Open browser console (F12) and check:
- Network tab for API calls
- Console for any errors
- Verify API calls are going to correct backend URL

---

## 🔧 Troubleshooting

### Backend Issues

**Problem: API returns 503 or doesn't start**
- Check Render/Railway/Heroku logs
- Verify `requirements.txt` is correct
- Ensure `main.py` is in root directory
- Check environment variables are set

**Problem: "No open ports detected" (Render)**
- Ensure your code reads `PORT` environment variable
- Check `main.py` uses: `port = int(os.getenv("PORT", 8000))`

**Problem: Build fails**
- Check build logs for specific errors
- Verify all dependencies in `requirements.txt`
- Ensure Python version is compatible

### Frontend Issues

**Problem: Frontend shows JSON instead of HTML**
- Check `vercel.json` routing configuration
- Ensure `index.html` is in root directory
- Verify routes are configured correctly

**Problem: API calls fail (CORS errors)**
- Check backend CORS settings in `main.py`
- Verify API URL in `index.html` is correct
- Check browser console for specific errors

**Problem: "API not found" errors**
- Verify backend is deployed and running
- Check backend URL in `index.html`
- Test backend directly using curl/Postman

---

## 📝 Quick Reference: Deployment URLs

After deployment, you should have:

- **Backend API**: `https://your-backend.onrender.com` (or Railway/Heroku)
- **Frontend**: `https://your-project.vercel.app` (or Netlify/GitHub Pages)
- **API Docs**: `https://your-backend.onrender.com/docs`

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Backend deployed (Render/Railway/Heroku)
- [ ] Backend health check works (`/health`)
- [ ] Backend API docs accessible (`/docs`)
- [ ] Frontend deployed (Vercel/Netlify/GitHub Pages)
- [ ] Frontend API URL updated in `index.html`
- [ ] Frontend can call backend API
- [ ] Test queries return results
- [ ] All endpoints tested

---

## 🚀 Next Steps After Deployment

1. **Set up custom domains** (optional)
2. **Monitor logs** for errors
3. **Set up alerts** for downtime
4. **Optimize performance** if needed
5. **Add analytics** (optional)

---

## 💡 Tips

- **Free Tier Limits**: 
  - Render: Free tier spins down after 15 min inactivity
  - Railway: Free tier has usage limits
  - Vercel: Free tier is generous for frontend

- **Keep Backend Alive** (Render):
  - Use a service like UptimeRobot to ping your API every 5 minutes
  - Or upgrade to paid plan for always-on

- **Environment Variables**:
  - Never commit `.env` files to GitHub
  - Always set secrets in platform dashboards

- **Monitoring**:
  - Check deployment logs regularly
  - Set up error tracking (Sentry, etc.)

