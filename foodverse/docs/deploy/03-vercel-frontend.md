# Step 3: Deploy the frontend on Vercel

Result: your **demo link** like `https://foodverse-ai.vercel.app`.

## 1. Sign up
Go to https://vercel.com, click **Sign Up**, then **Continue with GitHub**.

## 2. Import the project
1. Click **Add New**, then **Project**.
2. Find `foodverse-ai` and click **Import**.

## 3. Configure
1. **Root Directory**: click **Edit**, choose `frontend`, click **Continue**.
2. **Framework Preset**: should say **Vite**. If not, choose it.
3. Open **Environment Variables** and add:
   - Name: `VITE_API_URL`
   - Value: your Render URL from Step 2, with **no `/` at the end**
     (right: `https://foodverse-api.onrender.com`, wrong: `https://foodverse-api.onrender.com/`)
4. Click **Add**.

## 4. Deploy
Click **Deploy** and wait 1 to 2 minutes. When you see the confetti, click **Continue to Dashboard**.

## 5. Copy your demo link
On the project page, copy the address under **Domains**.

## Write this down
Demo link: `https://________.vercel.app`

## Common problems
| Problem | Fix |
|---|---|
| Build fails | Check Root Directory is `frontend`. |
| Page loads but every action fails | Normal until Step 4 is finished. |
| Changed `VITE_API_URL` later | Go to **Deployments**, open the latest, click **Redeploy**. Variables only apply on a new build. |

Next: `04-connect.md`
