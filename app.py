from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import current_user
from config import Config
from models import db, Admin, Student, Company, JobPosition, Application
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Load user
@login_manager.user_loader
def load_user(user_id):
    role, id = user_id.split("-")

    if role == "admin":
        return Admin.query.get(int(id))
    elif role == "student":
        return Student.query.get(int(id))
    elif role == "company":
        return Company.query.get(int(id))

    return None

with app.app_context():
    db.create_all()

    if not Admin.query.first():
        admin = Admin(
            username="admin",
            password=generate_password_hash("admin123")
        )
        db.session.add(admin)
        db.session.commit()

#MARK:AUTH
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #Admin
        admin = Admin.query.filter_by(username=email).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            session["role"] = "admin"
            return redirect("/admin/dashboard")

        #Student
        student = Student.query.filter_by(email=email).first()
        if student and check_password_hash(student.password, password):
            if not student.is_active:
                flash("Your account is deactivated.")
                return redirect("/login")
            login_user(student)
            session["role"] = "student"
            return redirect("/student/dashboard")

        #Company
        company = Company.query.filter_by(email=email).first()
        if company and check_password_hash(company.password, password):
            if not company.is_active:
                flash("Company account is deactivated.")
                return redirect("/login")
            if not company.is_approved:
                flash("Waiting for admin approval.")
                return redirect("/login")
            login_user(company)
            session["role"] = "company"
            return redirect("/company/dashboard")

        flash("Invalid credentials")
    return render_template("login.html")

#MARK:STUDENT REGISTRATION
@app.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"))
        education = request.form.get("education")
        skills = request.form.get("skills")

        resume_file = request.files.get("resume")
        resume_filename = None

        if resume_file and resume_file.filename != "":
            resume_filename = resume_file.filename
            resume_file.save(f"static/uploads/{resume_filename}")

        student = Student(
            name=name,
            email=email,
            password=password,
            education=education,
            skills=skills,
            resume=resume_filename
        )

    try:
        db.session.add(job)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash("Something went wrong", "danger")
        return redirect(request.url)

        flash("Registration successful. Please login.")
        return redirect("/login")

    return render_template("register_student.html")

#MARK:COMPANY REGISTRATION
@app.route("/register/company", methods=["GET", "POST"])
def register_company():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"))
        website = request.form.get("website")
        hr_contact = request.form.get("hr_contact")

        if Company.query.filter_by(email=email).first():
            flash("Email already exists")
            return redirect("/register/company")

        company = Company(
            name=name,
            email=email,
            password=password,
            website=website,
            hr_contact=hr_contact
        )
    try:
        db.session.add(company)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash("Something went wrong", "danger")
        return redirect(request.url)

        flash("Registration successful. Please wait for admin approval.")
        return redirect("/login")

    return render_template("register_company.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

#MARK:ADMIN DASHBOARD
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not isinstance(current_user, Admin):
        return redirect("/")

    search_query = request.args.get("search")
    student_query = Student.query
    company_query = Company.query

    if search_query:
        students = student_query.filter(Student.name.contains(search_query)).all()
        companies = company_query.filter(Company.name.contains(search_query)).all()
    else:
        students = student_query.all()
        companies = company_query.all()

    return render_template(
        "admin/dashboard.html",
        total_students=Student.query.count(), # Global counts usually stay the same
        total_companies=Company.query.count(),
        total_jobs=JobPosition.query.count(),
        total_applications=Application.query.count(),
        companies=companies,
        students=students,
        jobs=JobPosition.query.all()
    )

@app.route("/admin/approve_company/<int:id>")
@login_required
def approve_company(id):
    if not isinstance(current_user, Admin):
        return redirect("/")

    company = Company.query.get_or_404(id)
    company.is_approved = True
    db.session.commit()
    return redirect("/admin/dashboard")

@app.route("/admin/blacklist/<string:type>/<int:id>")
@login_required
def blacklist(type, id):
    if not isinstance(current_user, Admin):
        return redirect("/")

    if type == "company":
        company = Company.query.get_or_404(id)
        company.is_active = False

        # Close all company drives
        for job in company.jobs:
            job.status = "Closed"

    elif type == "student":
        student = Student.query.get_or_404(id)
        student.is_active = False

    db.session.commit()
    return redirect("/admin/dashboard")

@app.route("/admin/approve_drive/<int:id>")
@login_required
def approve_drive(id):
    if not isinstance(current_user, Admin):
        return redirect("/")

    job = JobPosition.query.get_or_404(id)
    job.status = "Approved"
    db.session.commit()

    return redirect("/admin/dashboard")

@app.route("/admin/reject_drive/<int:id>")
@login_required
def reject_drive(id):
    if not isinstance(current_user, Admin):
        return redirect("/")

    job = JobPosition.query.get_or_404(id)
    job.status = "Rejected"
    db.session.commit()

    return redirect("/admin/dashboard")


#MARK:STUDENT DASHBOARD
@app.route("/student/dashboard")
@login_required
def student_dashboard():
    if not isinstance(current_user, Student):
        return redirect("/")

    approved_jobs = JobPosition.query.filter_by(status="Approved").all()

    applied_jobs = Application.query.filter_by(
        student_id=current_user.id
    ).all()

    # 🔥 ADD THIS
    applied_job_ids = [app.job_id for app in applied_jobs]

    return render_template(
        "student/dashboard.html",
        jobs=approved_jobs,              
        applications=applied_jobs,       
        applied_job_ids=applied_job_ids  
    )

@app.route("/student/apply/<int:job_id>")
@login_required
def apply_job(job_id):
    if not isinstance(current_user, Student):
        return redirect("/")

    # Check duplicate
    existing = Application.query.filter_by(
        student_id=current_user.id,
        job_id=job_id
    ).first()

    if existing:
        flash("You have already applied for this drive.")
        return redirect("/student/dashboard")

    application = Application(
        student_id=current_user.id,
        job_id=job_id
    )

    try:
        db.session.add(application)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash("Something went wrong", "danger")
        return redirect(request.url)

    flash("Application submitted successfully!")
    return redirect("/student/dashboard")


#MARK:COMPANY DASHBOARD
@app.route("/company/dashboard")
@login_required
def company_dashboard():
    if not isinstance(current_user, Company):
        return redirect("/")

    jobs = JobPosition.query.filter_by(company_id=current_user.id).all()
    for job in jobs:
        job.application_count = Application.query.filter_by(job_id=job.id).count()

    return render_template(
        "company/dashboard.html",
        jobs=jobs
    )

@app.route("/company/create_drive", methods=["GET", "POST"])
@login_required
def create_drive():
    if not isinstance(current_user, Company):
        return redirect("/")

    if request.method == "POST":
        drive_name = request.form.get("drive_name")
        title = request.form.get("title")
        deadline_str = request.form.get("deadline")

        if not drive_name or not title or not deadline_str:
            flash("All fields including deadline are required!", "danger")
            return redirect(request.url)

        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()

        job = JobPosition(
            drive_name=drive_name,
            title=title,
            description=request.form.get("description"),
            eligibility=request.form.get("eligibility"),
            salary=request.form.get("salary"),
            location=request.form.get("location"),
            deadline=deadline,
            status="Pending",
            company_id=current_user.id
        )

        try:
            db.session.add(job)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("Something went wrong. Please try again.", "danger")
            return redirect(request.url)

        flash("Drive created!", "success")
        return redirect("/company/dashboard")

    return render_template("company/create_drive.html")

@app.route("/company/student/<int:student_id>")
@login_required
def view_student(student_id):
    if not isinstance(current_user, Company):
        return redirect("/")

    student = Student.query.get_or_404(student_id)
    return render_template("company/student_profile.html", student=student)

@app.route("/company/close_drive/<int:id>")
@login_required
def close_drive(id):
    if not isinstance(current_user, Company):
        return redirect("/")

    job = JobPosition.query.get_or_404(id)

    if job.company_id != current_user.id:
        return redirect("/")

    job.status = "Closed"
    db.session.commit()

    return redirect("/company/dashboard")

@app.route("/company/view_applications/<int:job_id>")
@login_required
def view_applications(job_id):
    if not isinstance(current_user, Company):
        return redirect("/")

    job = JobPosition.query.get_or_404(job_id)

    if job.company_id != current_user.id:
        return redirect("/")

    applications = Application.query.filter_by(job_id=job_id).all()

    return render_template(
        "company/applications.html",
        job=job,
        applications=applications
    )

@app.route("/company/update_application/<int:app_id>/<string:new_status>")
@login_required
def update_application(app_id, new_status):
    if not isinstance(current_user, Company):
        return redirect("/")

    application = Application.query.get_or_404(app_id)

    if application.job.company_id != current_user.id:
        return redirect("/")

    application.status = new_status
    db.session.commit()
    flash(f"Application marked as {new_status}")
    return redirect(f"/company/view_applications/{application.job_id}")


@app.route("/")
def home():
    if current_user.is_authenticated:
        if isinstance(current_user, Student):
            return redirect("/student/dashboard")
        elif isinstance(current_user, Company):
            return redirect("/company/dashboard")
    return render_template("home.html")

#MARK:ERROR HANDLERS
@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template("errors/500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)