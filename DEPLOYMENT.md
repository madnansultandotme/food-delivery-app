# Deployment Guide - Vercel

## Prerequisites
- Vercel Account
- Supabase Database Setup
- Environment variables configured

## Steps to Deploy

### 1. Connect Supabase Database
Ensure these environment variables are set in your Vercel project:
- `SUPABASE_POSTGRES_URL`
- `SUPABASE_JWT_SECRET`

### 2. Deploy to Vercel
\`\`\`bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
\`\`\`

### 3. Initialize Database
The database tables will be created automatically on first request to any endpoint.

### 4. Test Health Check
\`\`\`bash
curl https://your-app.vercel.app/api/health
\`\`\`

## Environment Variables
Set these in Vercel Project Settings > Environment Variables:

\`\`\`
SUPABASE_POSTGRES_URL=postgresql://...
SUPABASE_JWT_SECRET=your-jwt-secret
\`\`\`

## Monitoring
Monitor your API using Vercel Analytics and logs available in the Vercel Dashboard.
