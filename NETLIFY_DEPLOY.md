# Deploying to Netlify

This guide explains how to deploy the word puzzle game to Netlify.

## Prerequisites

1. A Netlify account (free tier works)
2. Git repository (GitHub, GitLab, or Bitbucket)
3. Your code pushed to the repository

## Important Notes

⚠️ **Python Functions on Netlify**: Netlify Functions primarily support JavaScript/TypeScript. Python support may be limited. Consider these alternatives:
- **Option A**: Convert functions to Node.js (recommended for Netlify)
- **Option B**: Use a different platform with better Python support (Vercel, Railway, Render)
- **Option C**: Use Netlify's experimental Python runtime (if available)

⚠️ **State Management Limitation**: The current implementation uses in-memory storage for puzzle state (`active_puzzles`). In Netlify's serverless environment, this means:
- Puzzle state is not shared between function invocations
- Puzzles may expire immediately after creation
- For production, you should use external storage (e.g., Netlify KV, Upstash Redis, or a database)

## Deployment Steps

### Option 1: Deploy via Netlify UI

1. **Push your code to Git**
   ```bash
   git add .
   git commit -m "Prepare for Netlify deployment"
   git push
   ```

2. **Connect to Netlify**
   - Go to [Netlify](https://app.netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Connect your Git provider and select your repository

3. **Configure Build Settings**
   - **Base directory**: (leave empty)
   - **Build command**: (leave empty or use `echo 'No build needed'`)
   - **Publish directory**: `static`

4. **Deploy**
   - Click "Deploy site"
   - Wait for deployment to complete

### Option 2: Deploy via Netlify CLI

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Login to Netlify**
   ```bash
   netlify login
   ```

3. **Initialize and Deploy**
   ```bash
   netlify init
   # Follow prompts:
   # - Create & configure a new site
   # - Team: Select your team
   # - Site name: (choose a name)
   # - Build command: (leave empty)
   # - Publish directory: static
   
   netlify deploy --prod
   ```

## Project Structure

The deployment uses this structure:
```
betterWordrow/
├── static/              # Frontend files (HTML, CSS, JS)
├── netlify/
│   └── functions/
│       └── api/
│           ├── puzzle.py    # GET /api/puzzle
│           └── check.py     # POST /api/check
├── puzzle_generator.py   # Core puzzle logic
├── wordlist.txt         # Word dictionary
└── netlify.toml         # Netlify configuration
```

## Configuration Files

### netlify.toml
- Configures function directory
- Sets up redirects for API routes
- Configures SPA routing

### Function Structure
- Functions are in `netlify/functions/api/`
- Each function exports a `handler(event, context)` function
- Functions automatically handle CORS

## Testing Locally

You can test Netlify Functions locally:

1. **Install Netlify CLI** (if not already installed)
   ```bash
   npm install -g netlify-cli
   ```

2. **Run Netlify Dev**
   ```bash
   netlify dev
   ```

3. **Access the site**
   - Frontend: http://localhost:8888
   - Functions: http://localhost:8888/.netlify/functions/api/puzzle

## Troubleshooting

### Functions Not Working

1. **Check function logs**
   - Go to Netlify Dashboard → Your Site → Functions
   - Check for errors in function logs

2. **Verify file paths**
   - Ensure `wordlist.txt` is in the repository root
   - Check that function files are in `netlify/functions/api/`

3. **Check Python version**
   - Netlify uses Python 3.9 by default
   - Verify in `netlify.toml`

### State Not Persisting

This is expected behavior with in-memory storage. For production:
- Use Netlify KV (key-value store)
- Use Upstash Redis
- Use a database (PostgreSQL, MongoDB, etc.)

### CORS Issues

CORS headers are included in the functions. If you still see issues:
- Check browser console for errors
- Verify function responses include CORS headers
- Test with `curl` or Postman

## Production Considerations

1. **External Storage**: Replace in-memory `active_puzzles` with external storage
2. **Error Handling**: Add more robust error handling and logging
3. **Rate Limiting**: Consider adding rate limiting to prevent abuse
4. **Monitoring**: Set up Netlify Analytics and function monitoring
5. **Environment Variables**: Use Netlify environment variables for configuration

## Alternative Deployment Options

### Option 1: Convert to Node.js Functions (Recommended for Netlify)

Netlify has excellent support for Node.js functions. Consider:
1. Convert `puzzle_generator.py` to JavaScript/TypeScript
2. Use Node.js functions instead of Python
3. Better performance and native support

### Option 2: Use Vercel (Better Python Support)

Vercel has excellent Python runtime support:
```bash
npm i -g vercel
vercel
```

### Option 3: Use Railway or Render

Both platforms support Python Flask apps natively:
- **Railway**: `railway up`
- **Render**: Connect GitHub repo, set build command to `pip install -r requirements.txt && python server.py`

### Option 4: Use Netlify Edge Functions

For better performance, consider migrating to Netlify Edge Functions (Deno runtime):
- Faster cold starts
- Better global distribution
- Different API structure
- Would require converting Python code to TypeScript/JavaScript

## Support

For issues:
- Check [Netlify Docs](https://docs.netlify.com/)
- Check function logs in Netlify Dashboard
- Review this project's README.md

