# Step 2: Deploy the backend on Render

Result: a **backend URL** like `https://foodverse-api.onrender.com`.

## 1. Sign up
Go to https://render.com and click **Get Started**, then **GitHub**. Allow access to your repositories.

## 2. Create the service from the blueprint
1. Click **New** (top right), then **Blueprint**.
2. Pick the repository `foodverse-ai`.
3. Render reads the file `render.yaml` and shows a service called `foodverse-api`.

## 3. Fill in the secrets
- `ANTHROPIC_API_KEY`: paste your key from Step 0.
- `CORS_ORIGINS`: leave it **empty** for now. You set it in Step 4.
- `CLAUDE_MODEL`: leave as it is.

## 4. Deploy
Click **Apply** and wait 5 to 10 minutes. The status turns to **Live** when done.

## 5. Test it
1. Copy the URL shown at the top of the service page.
2. Open `YOUR-URL/health` in a browser.
3. You should see: `{"status":"ok","version":"1.1.0"}`
4. Bonus: open `YOUR-URL/docs` to see all API endpoints.

## Write this down
Backend URL: `https://________.onrender.com`

## Notes
- Free services sleep when idle. The first request after a pause takes about a minute.
- The saved meal log resets when the service redeploys.

## Common problems
| Problem | Fix |
|---|---|
| Build fails | Open the **Logs** tab and read the last red lines. Send them to me if unsure. |
| `/health` shows an error page | Wait 2 minutes and refresh. The service may still be starting. |
| Blueprint not found | Make sure `render.yaml` is in the root of the repo (not inside a subfolder) |

Next: `03-vercel-frontend.md`
