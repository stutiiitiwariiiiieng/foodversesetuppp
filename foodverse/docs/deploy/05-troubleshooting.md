# Step 5: Troubleshooting

| What you see | Likely cause | Fix |
|---|---|---|
| "Failed to fetch" | CORS or wrong API URL | Check `CORS_ORIGINS` on Render matches your Vercel link exactly, then check `VITE_API_URL` on Vercel. Redeploy Vercel after any change. |
| Browser console says "blocked by CORS policy" | `CORS_ORIGINS` has a trailing `/` or is `http` | Remove the `/`, use `https`, save, wait for redeploy |
| Very slow first request | Free backend was asleep | Open `/health` first, wait about a minute |
| "AI service error" or 502 | Wrong key, no credit, or wrong model name | Check `ANTHROPIC_API_KEY` on Render, check your Anthropic credit. If the model name is rejected, set `CLAUDE_MODEL` to a model your key can use. |
| 413 "too large" | File over the limit | Photos: max 10 MB. Videos: max 200 MB. Use a short clip. |
| Hygiene video times out | Video too long | Use a clip of 20 to 30 seconds |
| My week is empty | Meal log reset or nothing scanned | Scan a meal again. Free tier storage resets on redeploy. |
| Vercel build fails | Wrong root directory | Settings > General > Root Directory = `frontend` |
| Render build fails | See Logs tab | Read the last red lines. Send them to me. |

## Where to find logs
- Render: your service > **Logs**
- Vercel: your project > **Deployments** > click the latest > **Build Logs**
- Browser: press F12 > **Console** and **Network** tabs

Next: `06-submit.md`
