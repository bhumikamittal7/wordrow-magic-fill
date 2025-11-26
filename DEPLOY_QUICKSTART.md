# Quick Start: Deploy to Netlify

## ⚠️ Important: Python Functions Limitation

Netlify Functions have **limited Python support**. The Python functions in this repo may not work directly. 

## Recommended Approach: Use Vercel Instead

Vercel has excellent Python support and is very similar to Netlify:

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

Vercel will automatically detect your Flask app and deploy it.

## If You Must Use Netlify

### Option 1: Try Python Functions (May Not Work)

1. Push code to GitHub
2. Connect to Netlify
3. Set publish directory to `static`
4. Deploy and test

If Python functions don't work, see Option 2.

### Option 2: Convert to Node.js (Recommended)

1. Convert `puzzle_generator.py` to JavaScript
2. Use the Node.js function templates
3. Deploy to Netlify

### Option 3: Use Different Platform

- **Railway**: Best for Flask apps
- **Render**: Easy Python deployment  
- **Fly.io**: Good Python support
- **Heroku**: Traditional option (paid)

## Quick Deploy Commands

### Netlify (if Python works)
```bash
netlify init
netlify deploy --prod
```

### Vercel (recommended)
```bash
vercel
```

### Railway
```bash
railway login
railway init
railway up
```

## File Structure for Deployment

```
betterWordrow/
├── static/              # Frontend (served directly)
├── netlify/
│   └── functions/       # Serverless functions
├── puzzle_generator.py  # Core logic
├── wordlist.txt        # Dictionary
└── netlify.toml        # Netlify config
```

## What Gets Deployed

- ✅ `static/` folder → Served as static files
- ✅ `netlify/functions/` → Serverless functions
- ✅ `puzzle_generator.py` → Used by functions
- ✅ `wordlist.txt` → Used by functions
- ❌ `server.py` → Not used (replaced by functions)
- ❌ `generate_*.py` → Not needed for deployment

## Testing Locally

```bash
# Netlify
netlify dev

# Vercel  
vercel dev
```

## Need Help?

- See `NETLIFY_DEPLOY.md` for detailed instructions
- Check platform-specific documentation
- Consider using Vercel for better Python support

