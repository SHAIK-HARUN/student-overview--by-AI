# Teacher Academic Intelligence & Profiling Portal (XAI)

A modern, responsive web application designed for **Class Teachers** to record student academic and Online Judge submission metrics, predict performance profiles (`Excellent`, `Good`, `Average`, `Poor`) using Explainable Artificial Intelligence (XAI) ensemble models, and automatically dispatch diagnostic feedback reports to **Parents** via **Email** (`shaikashfaq911@gmail.com`) and **WhatsApp** (`+91 9182257621`).

---

## 🌟 Key Architecture & Workflows

### 1. Teacher Portal (`/register/`, `/login/`, `/dashboard/`)
1. **Teacher Registration**:
   - Class Teachers create their own accounts with:
     - Full Name & Username
     - Official Email & Phone / WhatsApp number
     - Department (e.g. Computer Science) & Designation (e.g. Class Teacher)
     - Campus / Office location
2. **Teacher Dashboard**:
   - Displays real-time statistics: Total Students Managed, Predictions Run, Excellent Profiles, and Profiles Needing Attention.
   - Quick actions to Add Student & Predict, View All Students, and access Full Dispatch History.
3. **Add Student Details & Predict (`/add-student/`)**:
   - Teachers enter complete student attributes as requested:
     - `id` / `Fid` (Student Roll No / Online Judge ID)
     - `student_name` (Student Full Name)
     - `age`
     - `gender`
     - `lunch` (standard, free/reduced)
     - `parental_level_of_education` (bachelor's, master's, associate's, some college, high school, some high school)
     - `degree_t` (Sci&Tech, Comm&Mgmt, Others)
     - `race_ethnicity` (group A, group B, group C, group D, group E)
     - `test_preparation_course` (completed, none)
     - `math_score`, `reading_score`, `writing_score` (0 – 100 with interactive range sliders)
     - `Internships` (0, 1, 2, 3+)
     - `solving_tasks_by_time` (1 = On Time, 0 = Late)
     - `taks_submitted_on_date` (1 = On Date, 0 = Delayed)
     - **Parent Contact Information**: `parent_name`, `parent_phone` (WhatsApp), `parent_email`.
4. **AI Prediction & Automated Parent Dispatch**:
   - Predicts profile (`Excellent`, `Good`, `Average`, `Poor`) via a voting ensemble of 7 machine learning models.
   - Generates Explainable AI (XAI) strengths, areas needing attention, and study recommendations.
   - **Email to Parent**: Sent from `shaikashfaq911@gmail.com`.
   - **WhatsApp to Parent**: Formatted alert sent from college number `+91 9182257621`, with 1-click Direct WhatsApp trigger button.
5. **Regenerate & Direct Accumulation**:
   - Teachers can click **"Regenerate Result & Re-notify Parents"** on any student result to recalculate and instantly re-dispatch updated reports to the parents.

---

### 2. Service Provider Admin Dashboard (`/admin-panel/`)
- **Credentials**: `Admin` / `Admin`
- **Model Training (`/admin-panel/train/`)**:
  - Trains and benchmarks 7 algorithms on `Datasets.csv`:
    1. Artificial Neural Network (ANN / MLPClassifier)
    2. Naive Bayes (MultinomialNB)
    3. Support Vector Machine (Linear SVC)
    4. Logistic Regression
    5. Gradient Boosting Classifier
    6. Decision Tree Classifier
    7. K-Nearest Neighbors (KNN)
- **Advanced Interactive Charts (`/admin-panel/charts/`)**:
  - **Bar Chart**: Algorithm accuracy comparison.
  - **Line Chart**: Multi-metric performance trends across models.
  - **Pie & Doughnut Charts**: Student profile category distribution.
  - **Multi-Metric Radar Chart**: Precision, Recall, Accuracy, and F1-score comparison.
  - **Polar Area Chart**: Profile distribution.
  - **Execution Time Bar Chart**: Model training time benchmarks.
  - **Bubble Chart**: Accuracy vs. Execution time trade-off.
- **Auditing**: View all registered Class Teachers, Student Records, Predictions, and Notification audit logs.

---

## 🚀 How to Run

```bash
cd "d:\Final year code\Identifying Student Profiles within Online Judge systems using Explainable Artificial Intelligence-20240202T085446Z-001 (1)\student_portal"
python manage.py runserver
```

Then visit:
- **Home Page**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Teacher Login**: [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
- **Teacher Registration**: [http://127.0.0.1:8000/register/](http://127.0.0.1:8000/register/)
- **Admin / Service Provider**: [http://127.0.0.1:8000/admin-panel/login/](http://127.0.0.1:8000/admin-panel/login/)
