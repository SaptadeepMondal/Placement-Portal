# 🎓 Placement Portal

A full-stack web application built with Flask that streamlines campus recruitment by connecting students and companies on a single platform. It enables efficient job application management, candidate tracking, and recruitment workflows.

---

## 🚀 Overview

The Placement Portal is designed to simplify the placement process for students, recruiters, and administrators. It provides a centralized system where:

- Students can explore and apply for jobs
- Companies can manage hiring drives and candidates
- Admins can control and verify company access

---

## ✨ Features

### 👨‍🎓 Students
- Register & login
- Apply to placement drives
- Upload resume
- Track application status

### 🏢 Companies
- Create placement drives
- View applicants
- Shortlist / reject / hire candidates

### 🛠 Admin
- Approve or reject company registrations

---

## 🧰 Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite (SQLAlchemy)
- **Frontend:** HTML, Bootstrap
- **Auth:** Flask-Login
- **Security:** Werkzeug hashing

---

##🔒 Security Features
- Password hashing using Werkzeug
- Session-based authentication with Flask-Login
- Role-based access (Admin / Student / Company)

---

## 📦 Installation & Setup

Follow these steps to run the project locally:

```bash
# 1. Clone the repository
git clone https://github.com/SaptadeepMondal/Placement-Portal.git

# 2. Navigate to the project folder
cd Placement-Portal

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

---

## 📁 Project Structure
```
placement-portal/
│── app.py
│── models.py
│── templates/
│── static/
│── requirements.txt
│── README.md
```

---

## 💡 Future Improvements

- Email notifications for application updates
- Resume parsing & ranking system
- Admin analytics dashboard
- API integration for job listings
- Deployment (AWS / Heroku / Docker)

---

## 🧠 Learnings

Through this project, I gained hands-on experience with:
- Backend development using Flask
- Database modeling with SQLAlchemy
- User authentication and session management
- Building real-world CRUD applications

More improvements are on the way 🚀

---
