# Render.com Deployment - ArchaeoScan Backend

## 🚀 Super Simple Deployment (2 minutes!)

### 📋 Prerequisites
1. GitHub account
2. Render.com account (free)

---

## 🔧 Step 1: Push to GitHub

```bash
git add .
git commit -m "Add Render.com deployment config"
git push origin main
```

---

## 🌐 Step 2: Deploy on Render

1. **Go to:** https://render.com/
2. **Sign up** with GitHub
3. **Click "New +" → "Web Service"**
4. **Connect GitHub repository:** `Dyman17/archaeoscan-1`
5. **Configure:**
   - **Name:** `archaeoscan-backend`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

6. **Environment Variables:**
   ```
   PYTHONPATH = /opt/render/project/backend
   SECRET_KEY = archaeoscan-secret-key-2024
   DATABASE_URL = (will be auto-filled by Render)
   ```

7. **Click "Deploy Web Service"**

---

## 🗄️ Step 3: Add Database

1. **Click "New +" → "PostgreSQL"**
2. **Name:** `archaeoscan-db`
3. **Plan:** Free
4. **Click "Create Database"**

---

## 🎯 Step 4: Connect Database

1. **Go to your web service**
2. **Environment tab**
3. **Add DATABASE_URL** from database connection details
4. **Redeploy**

---

## 🌐 URLs After Deployment

**Backend:** `https://archaeoscan-backend.onrender.com`
**API Docs:** `https://archaeoscan-backend.onrender.com/docs`
**Health:** `https://archaeoscan-backend.onrender.com/api/status`

---

## 📡 Frontend Integration

Update frontend URLs:
```typescript
// frontend/src/context/AppContext.tsx
websocketUrl: 'wss://archaeoscan-backend.onrender.com/ws'
```

---

## ✅ Benefits vs Railway/Fly.io

✅ **EASIEST** - GitHub auto-deploy  
✅ **FASTEST** - 2 minutes setup  
✅ **FREE** - 750 hours/month  
✅ **NO CLI** - Web interface only  
✅ **AUTO HTTPS** - SSL included  
✅ **BUILT-IN DB** - PostgreSQL free  

---

## 🔄 Commands

```bash
# Update deployment
git push origin main

# View logs
# Render dashboard → Logs tab

# Redeploy
# Render dashboard → Manual Deploy
```

---

## 🐛 Troubleshooting

**Build fails:**
- Check Python version in requirements.txt
- Verify PYTHONPATH env var

**App not starting:**
- Check logs in Render dashboard
- Verify start command

**Database connection:**
- Copy DATABASE_URL from database tab
- Add to web service environment

---

## 📊 Monitoring

All in Render dashboard:
- Logs
- Metrics  
- Status
- Environment variables

**THAT'S IT! Render.com is the easiest!** 🚀
