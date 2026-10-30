# Step 4: Connect frontend and backend

Without this step the browser blocks the requests (a CORS error).

## 1. Allow your frontend on the backend
1. Open your service on Render, then **Environment**.
2. Set `CORS_ORIGINS` to your Vercel link, exactly as in the address bar:
   `https://your-project.vercel.app`
   - No `/` at the end.
   - Use `https`.
3. Click **Save Changes**. Render redeploys (1 to 3 minutes).

## 2. Test the whole app
1. Open `YOUR-RENDER-URL/health` first to wake the backend.
2. Open your Vercel link.
3. **Meal scan**: upload a food photo, click **Analyze meal**, and check you get calories and macros.
4. **Freshness**: upload a fruit photo and check you get a status.
5. **Recipes**: type "vegetable upma", click **Get recipe**.
6. **Meal plan**: click **Build my plan**.
7. **My week**: confirm your scanned meal appears.

## Pass condition
All of the above return results with no red error box.

Next: `05-troubleshooting.md` (only if something failed), otherwise `06-submit.md`
