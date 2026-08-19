# Deploy the Web App (Free)

Two free options — pick whichever you prefer.

---

## Option A: Streamlit Community Cloud (recommended)

**Result:** `https://your-app-name.streamlit.app`

### Step 1 — Push to GitHub

```bash
cd library-validator
git init
git add .
git commit -m "Library metadata validator web app"
```

Create a new repo on GitHub (github.com → New repository → name it `library-validator`).

Then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/library-validator.git
git branch -M main
git push -u origin main
```

### Step 2 — Deploy on Streamlit

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with GitHub
3. Click **New app**
4. Select your `library-validator` repo
5. Set **Main file path** to `app.py`
6. Click **Deploy**

Your app goes live in ~2 minutes at a URL like:
`https://library-validator.streamlit.app`

---

## Option B: Hugging Face Spaces

**Result:** `https://huggingface.co/spaces/YOUR_USERNAME/library-validator`

1. Go to **[huggingface.co/new-space](https://huggingface.co/new-space)**
2. Name: `library-validator`
3. SDK: **Streamlit**
4. Click **Create Space**
5. Upload these files (or connect GitHub):
   - `app.py`
   - `requirements.txt`
   - `src/` folder
   - `samples/` folder
   - `.streamlit/config.toml`

Or clone and push:

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/library-validator
cp -r app.py requirements.txt src samples .streamlit library-validator/
cd library-validator
git add . && git commit -m "Initial deploy" && git push
```

---

## Test locally first

```bash
cd library-validator
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Resume link

Once deployed, add the live URL to your resume:

> **Library Metadata Validator** — [your-app.streamlit.app](https://your-app.streamlit.app)  
> Built a Python data validation tool to parse and audit library inventory batches, identifying metadata anomalies, duplicate barcodes, and invalid tags.
