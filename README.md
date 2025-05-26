# 🕵️ Monitoring Suspicious Discussions (MSD)

Welcome to Monitoring Suspicious Discussions!
This project is designed to monitor and flag potentially suspicious conversations in online forums using natural language processing.

---

## 🤔 What is MSD?

**Monitoring Suspicious Discussions** is a smart forum surveillance tool built for detecting shady or harmful discussions.

Minimizes manual moderation — this project automates the process by:

* Scanning text posts.
* Identifying violent/threatening/abusive language.
* Storing and flagging them for admin review only when the context may change the sensitivity of the post.

It’s powered by **Flask**, **Jinja2**, and **MySQL**. Clean, fast, and effective.

---

## 🛠️ Software Requirements

To run MSD locally, you’ll need:

1. **Python 3.x**
2. **Flask**
3. **MySQL Server**
4. **VS Code** or any editor
5. A web browser (Chrome recommended)

---

## 📂 Setting Up MSD on Your System

1. Clone or download this repo.

2. Inside the main folder, make sure you have:

   * `templates/` (for Jinja2 HTML templates)
   * `app.py` (Flask server)
   * `msd.sql` (database schema)
   * `suspicious_model/` (optional logic/ML models)

3. In MySQL:

   * Create a database named `msd`
   * Import `msd.sql` to create necessary tables like `users`, `posts`, and `admins` and make sure to add some data to these tables, either by registering and creating posts (Recommended) or by manually giving them

---

## ▶️ Running MSD

1. Install Python dependencies:

   ```bash
   pip install flask
   ```
   
    ```bash
   pip install flask_mysql
   ```
     
    ```bash
   pip install flask_bcrypt
   ```

    ```bash
   pip install nltk
   ```

2. Edit `app.py` and update your DB credentials if needed.

3. Run the server:

   ```bash
   python app.py
   ```

4. Open your browser and go to:

   ```
   http://localhost:5000/
   ```

---

## 💡 How MSD works

1. You can register/login as a user or admin.
2. User can submit new posts on the forum.
3. The system checks each post:
   * Matches against a list of suspicious keywords
   * (Optional) Applies NLP logic to evaluate tone
4. Suspicious posts are flagged and stored in the database.
5. Admins can log in and view flagged content from the dashboard and moderate them.

---

## 👥 Project Contributors

Proudly built by:

* [Abhilash037415](https://github.com/Abhilash037415)
* [AlapatiVamsi05](https://github.com/AlapatiVamsi05)
* [VarunSai2005](https://github.com/VarunSai2005)
* [ksamuel-soul](https://github.com/ksamuel-soul)
* [rohitsripathi9](https://github.com/rohitsripathi9)

We kept it simple, efficient, and on point.
No login traps. No subscriptions. Just pure suspicious detection.


---

Enjoy using MSD!
Keep the forums clean, stay safe, and don’t be sus. 🕶️
