# Zero to deployed

Result: a GitHub repo link and a live demo link. Free tiers are enough.

## 1. Run it locally first
```
./scripts/setup.sh          # add your ANTHROPIC_API_KEY to backend/.env when asked
make check && make test
make backend                # terminal 1
make frontend               # terminal 2  -> http://localhost:5173
```
If a feature works here, it will work deployed.

## 2. Put the code on GitHub  (this gives you the GitHub link)
1. Create an account at github.com, then click New repository. Name: `foodverse-ai`, Public, leave "Add README" unticked.
2. In the project folder:
```
git init
git add .
git commit -m "FoodVerse AI: initial version"
git branch -M main
git remote add origin https://github.com/<your-username>/foodverse-ai.git
git push -u origin main
```
3. Check that `backend/.env` is NOT in the repo (it is in .gitignore). Never commit your API key.
4. Your GitHub link: `https://github.com/<your-username>/foodverse-ai`

## 3. Deploy the backend on Render
1. Sign in at render.com with GitHub. New > Blueprint > pick `foodverse-ai`. It reads `render.yaml`.
2. Set `ANTHROPIC_API_KEY` to your key. Leave `CORS_ORIGINS` blank for now.
3. Deploy. When it is live, open `https://<name>.onrender.com/health`. You should see `{"status":"ok"...}`.
4. Note the URL. API docs are at `/docs`.

Free-tier notes: the service sleeps after idle time (first request takes about 50 seconds), and the SQLite meal log resets on redeploy. For a permanent log, use Render PostgreSQL or an AWS database.

## 4. Deploy the frontend on Vercel
1. Sign in at vercel.com with GitHub. Add New > Project > import `foodverse-ai`.
2. Set Root Directory to `frontend`. Framework: Vite (auto-detected).
3. Environment variable: `VITE_API_URL` = your Render URL (no trailing slash).
4. Deploy. Your demo link is `https://<project>.vercel.app`.

## 5. Connect them
1. In Render > foodverse-api > Environment, set `CORS_ORIGINS` to your exact Vercel URL (no trailing slash). Save; it redeploys.
2. Open the Vercel URL, upload a meal photo, and confirm it returns results.

## 6. Final checks before you submit
- [ ] Meal scan, Freshness, Recipes, Kitchen assistant, Meal plan, My week all work on the live link
- [ ] Hygiene works with a short clip (under about 30 seconds, small file)
- [ ] README has screenshots and the live link
- [ ] No API key in the repo (search for `sk-ant`)
- [ ] Wake the free backend by opening `/health` a minute before any demo

## Alternative: AWS
If your course requires AWS: backend with App Runner (build from the `backend` Dockerfile, set env vars), frontend with S3 static hosting + CloudFront (`cd frontend && VITE_API_URL=<apprunner url> npm run build`, upload `dist/`). Store the key in Secrets Manager.

## Submission snippet
- Project: FoodVerse AI
- GitHub: https://github.com/<your-username>/foodverse-ai
- Demo: https://<project>.vercel.app
- Stack: React, FastAPI, Python, OpenCV, Claude (vision + LLM)
