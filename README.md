# Teacher & Student Academic Intelligence Portal (XAI-Driven)

A modern Django web portal powered by Explainable Artificial Intelligence (XAI) and ensemble machine learning algorithms to evaluate student performance profiles and automatically dispatch academic feedback notifications to parents and teachers via Email (Gmail SMTP) and WhatsApp.

---

## 🚀 Key Features

1. **Teacher Portal**:
   - **Simple Teacher Authentication**: Sign in using **Username only** (no email requested during login).
   - **Student Record Intake**: Full entry covering all 15 parameters:
     - `id`, `Fid`, `age`, `gender`, `lunch`, `parental_level_of_education`, `degree_t`, `race_ethnicity`, `test_preparation_course`, `math_score`, `reading_score`, `writing_score`, `Internships`, `solving_tasks_by_time`, `taks_submitted_on_date`.
   - **AI Ensemble Prediction**: Generates profile classification (`Excellent`, `Good`, `Average`, `Poor`) with automated explainable AI (XAI) diagnostics.
   - **Automated Re-dispatch**: Whenever a teacher updates or regenerates a result, updated academic reports are immediately accumulated and dispatched to the student's parents.

2. **Automated Notification System**:
   - **Official College Email Sender**: `shaikashfaq911@gmail.com`
   - **Official College WhatsApp Sender**: `+91 9182257621`
   - Formatted parent reports with academic score cards, performance categories, and strengths/weaknesses breakdown.
   - Fallback `wa.me` instant dispatch links generated for one-click manual or automated delivery.

3. **Service Provider / Admin Panel**:
   - Credentials: Username `Admin` / Password `Admin`.
   - Visual algorithm evaluation suite featuring **7 Algorithms**:
     - Multilayer Perceptron (MLP/ANN)
     - Naive Bayes
     - Linear Support Vector Machine (Linear SVC)
     - Logistic Regression
     - Gradient Boosting Classifier
     - Decision Tree Classifier
     - K-Nearest Neighbors (KNN)
   - Interactive visualizations via **Chart.js**: Line charts, Bar charts, Pie charts, Radar charts, Doughnut charts, and Polar Area charts.
   - System audit trail with real-time delivery logs of all emails and WhatsApp notifications.

---

## 🛠️ Tech Stack & Deployment Readiness

- **Framework**: Django 5.x
- **Frontend**: Bootstrap 5, Bootstrap Icons, Chart.js
- **Machine Learning**: Scikit-learn, Pandas, NumPy
- **Static Asset Serving**: Whitenoise 6.x (configured with `CompressedManifestStaticFilesStorage`)
- **Serverless Adapter**: Mangum + Netlify Functions (`netlify/functions/handler.py`)
- **Production Server**: Gunicorn (Procfile included)

---

## 📦 How to Push to GitHub

From the `student_portal` directory:

```bash
# Check current commit
git status

# Add your GitHub repository as remote origin (replace with your repository URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

---

## 🌐 Deployment Instructions

### Option 1: Deploying to Netlify
1. Connect your GitHub repository to [Netlify](https://app.netlify.com/).
2. Netlify will automatically detect `netlify.toml`:
   - **Build command**: `python -m pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput`
   - **Publish directory**: `staticfiles`
   - **Functions directory**: `netlify/functions`
3. Under **Site Configuration > Environment Variables**, add:
   - `EMAIL_HOST_USER`: `shaikashfaq911@gmail.com`
   - `EMAIL_HOST_PASSWORD`: `<your-16-char-gmail-app-password>`
   - `COLLEGE_WHATSAPP_NUMBER`: `+919182257621`
   - `SECRET_KEY`: `<your-django-secret-key>`
4. Trigger deploy.

> **Note on Netlify Serverless Storage**: Netlify functions operate in an ephemeral AWS Lambda runtime. The project settings automatically handle this by routing the SQLite database to `/tmp/db.sqlite3` and running migrations automatically on cold start. For persistent multi-user databases across global Lambda restarts, connecting an external database URL (e.g. Supabase, Neon, or Railway PostgreSQL) via `DATABASE_URL` is recommended.

### Option 2: Deploying to Render / Railway / PythonAnywhere (Recommended for persistent Django SQLite/Postgres)
1. Link your GitHub repo to **Render** or **Railway**.
2. Set Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
3. Set Start Command: `gunicorn student_portal.wsgi:application`
4. The included `Procfile` is recognized out of the box.

---

## 🔐 Default Admin Credentials
- **URL**: `/admin-portal/login/`
- **Username**: `Admin`
- **Password**: `Admin`
