# www.jimgabriel.com

Portfolio & marketing site for **Jim Gabriel's** indie games and interactive apps.

Built as a lightweight, zero-dependency static site designed for **GitHub Pages** and **GitHub Desktop**.

## Project Structure

```text
jimgabriel.com/
├── data/apps.json           # Single source of truth for all apps, links & copy
├── scripts/generate.py      # Regenerates all HTML pages from data/apps.json (built-in Python 3)
├── assets/apps/<slug>/      # App icons and screenshots
├── css/styles.css           # Dark indie-studio theme & per-app accent system
├── js/main.js               # Gallery scroll controls & accessible lightbox
├── index.html               # Generated homepage
├── rock-paper-carnage/      # Generated marketing page (/rock-paper-carnage/)
├── plasma-globe/            # Generated marketing page (/plasma-globe/)
├── school-time/             # Generated marketing page (/school-time/)
├── CNAME                    # Custom domain configuration (www.jimgabriel.com)
└── sitemap.xml              # Generated search-engine sitemap
```

## How to Update the Site

### 1. Add a new game or app
1. Create a folder for its images: `assets/apps/<your-slug>/` (add `icon.jpg` and screenshots).
2. Add a new entry to the `"apps"` array in `data/apps.json`.
3. Run the generator in Terminal:
   ```bash
   python3 scripts/generate.py
   ```
4. Commit and click **Push origin** in **GitHub Desktop** — GitHub Pages updates automatically in ~1 minute.

### 2. Turn on a live Android / Google Play link
In `data/apps.json`, find the app's `"android"` block and change:
```json
"android": {
  "status": "live",
  "url": "https://play.google.com/store/apps/details?id=YOUR_PACKAGE_ID"
}
```
Then run `python3 scripts/generate.py` and push via GitHub Desktop. The *"Android Coming Soon"* badge automatically switches to a live **Get on Google Play** button.

## Preview Locally

```bash
python3 -m http.server 8000
```
Open `http://localhost:8000` in your browser.

## Deploy to GitHub Pages (with GitHub Desktop)

1. Open **GitHub Desktop** → **File → Add Local Repository…** → select this folder (`jimgabriel.com`) and initialize/publish it as a **public** repository on GitHub (e.g., `jimgabriel.com`).
2. On GitHub.com, open your repo → **Settings → Pages**:
   - **Source**: Deploy from a branch
   - **Branch**: `main` / `/ (root)` → click **Save**
   - **Custom domain**: `www.jimgabriel.com` (automatically read from `CNAME`) → check **Enforce HTTPS** once DNS propagates.
3. At your domain registrar's DNS settings for `jimgabriel.com`:
   - Add a **CNAME** record: Host `www` → Value `<your-github-username>.github.io`
   - (Optional for apex `jimgabriel.com` redirect) Add **A** records for `@` pointing to GitHub Pages IPs:
     - `185.199.108.153`
     - `185.199.109.153`
     - `185.199.110.153`
     - `185.199.111.153`
