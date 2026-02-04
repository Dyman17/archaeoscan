# Fly.io Deployment Instructions

## 🚀 Deploy ArchaeoScan Backend to Fly.io

### Prerequisites
1. Install Fly CLI: https://fly.io/docs/hands-on/start/install-flyctl/
2. Sign up/login: `fly auth login`

### 📦 Deployment Steps

#### 1. Initialize Fly App
```bash
cd backend
fly launch --no-deploy
```

#### 2. Configure Environment Variables
```bash
fly secrets set DATABASE_URL="postgresql://user:pass@host:5432/dbname"
fly secrets set SECRET_KEY="your-secret-key"
```

#### 3. Deploy
```bash
fly deploy
```

#### 4. Check Status
```bash
fly status
fly logs
```

### 🔧 Configuration

**fly.toml** - Main configuration file
- Python 3.11 runtime
- 256MB RAM (free tier)
- Port 8080
- Health checks enabled

**Dockerfile** - Container build
- Python 3.11 slim base
- System dependencies for OpenCV
- Optimized layer caching

### 🌐 URLs

After deployment:
- **Backend URL**: `https://archaeoscan-backend.fly.dev`
- **API Docs**: `https://archaeoscan-backend.fly.dev/docs`
- **Health Check**: `https://archaeoscan-backend.fly.dev/`

### 📡 Frontend Integration

Update frontend URLs:
```typescript
// frontend/src/context/AppContext.tsx
websocketUrl: 'wss://archaeoscan-backend.fly.dev/ws'
```

### 🔄 Commands

```bash
# Deploy updates
fly deploy

# View logs
fly logs

# SSH into machine
fly ssh console

# Restart
fly apps restart archaeoscan-backend

# Scale up/down
fly scale count 1
```

### 🎯 Benefits vs Railway

✅ **Faster builds** - Docker caching
✅ **Better free tier** - 160 hours/month
✅ **More control** - Custom Dockerfile
✅ **Better logs** - Real-time streaming
✅ **Global CDN** - Edge locations

### 🐛 Troubleshooting

**Build fails:**
```bash
fly deploy --build-arg PYTHON_VERSION=3.11
```

**App not starting:**
```bash
fly logs --recent
fly status
```

**Memory issues:**
```bash
fly scale memory 512
```

### 📊 Monitoring

```bash
# Metrics
fly metrics

# Status
fly status
```
