# Step 1: Upload the code to GitHub

Result: your **GitHub link**.

## 1. Create an empty repository
1. Log in to GitHub and click **+** (top right), then **New repository**.
2. Repository name: `foodverse-ai`
3. Choose **Public**.
4. Leave "Add a README", ".gitignore" and "license" all **unticked**.
5. Click **Create repository**.

## 2. Push the code
Open a terminal **inside the unzipped `foodverse` folder** and run these one at a time.
Replace `YOUR-USERNAME` with your GitHub username.

```
git init
git add .
git commit -m "first version"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/foodverse-ai.git
git push -u origin main
```

If asked to log in, use your GitHub username and a **personal access token** as the password
(GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic) > Generate, tick `repo`).

## 3. Check it
- Refresh the repo page. You should see the folders `backend`, `frontend`, `docs` and more.
- Make sure there is **no** file named `.env` inside `backend`. (Only `.env.example` should be there.)

## Your GitHub link
`https://github.com/YOUR-USERNAME/foodverse-ai`

## Common problems
| Problem | Fix |
|---|---|
| `git: command not found` | Install Git (Step 0), reopen the terminal |
| `remote origin already exists` | Run `git remote remove origin`, then the `remote add` line again |
| Login fails | Use a personal access token, not your account password |

Next: `02-render-backend.md`
