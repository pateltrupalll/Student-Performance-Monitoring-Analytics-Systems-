from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Module, Performance, Quiz, Attendance, Leave
from datetime import datetime, date, timedelta, timezone
from sqlalchemy import func, extract
from flask import Blueprint

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return redirect(url_for('main.login'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        return redirect(url_for('main.student_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            else:
                return redirect(url_for('main.student_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


# ==================== STUDENT DASHBOARD ====================
@main.route('/student-dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return redirect(url_for('main.admin_dashboard'))

    recent_results = db.session.query(
        Performance.score,
        Performance.completed_at,
        Performance.module_id,
        Module.module_name
    ).join(Module, Performance.module_id == Module.id) \
        .filter(Performance.student_id == current_user.id) \
        .order_by(Performance.completed_at.desc()).limit(5).all()

    recent_performances = []
    for result in recent_results:
        recent_performances.append({
            'score': result.score,
            'completed_at': result.completed_at,
            'module_id': result.module_id,
            'module_name': result.module_name
        })

    avg_score = db.session.query(func.avg(Performance.score)) \
                    .filter_by(student_id=current_user.id).scalar() or 0

    current_week = datetime.now(timezone.utc).isocalendar()[1]
    weekly_score = db.session.query(func.avg(Performance.score)) \
                       .filter_by(student_id=current_user.id) \
                       .filter(Performance.week_number == current_week).scalar() or 0

    modules_completed = Performance.query.filter_by(student_id=current_user.id).count()

    current_month = datetime.now(timezone.utc).month
    current_year = datetime.now(timezone.utc).year

    total_days = Attendance.query.filter_by(
        student_id=current_user.id
    ).filter(
        extract('month', Attendance.date) == current_month,
        extract('year', Attendance.date) == current_year
    ).count()

    present_days = Attendance.query.filter_by(
        student_id=current_user.id,
        status='Present'
    ).filter(
        extract('month', Attendance.date) == current_month,
        extract('year', Attendance.date) == current_year
    ).count()

    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

    recent_attendance = Attendance.query.filter_by(student_id=current_user.id) \
        .order_by(Attendance.date.desc()).limit(7).all()

    pending_leaves = Leave.query.filter_by(
        student_id=current_user.id,
        status='Pending'
    ).count()

    approved_leaves = Leave.query.filter_by(
        student_id=current_user.id,
        status='Approved'
    ).count()

    recent_leaves = Leave.query.filter_by(student_id=current_user.id) \
        .order_by(Leave.applied_on.desc()).limit(5).all()

    return render_template('student_dashboard.html',
                           recent_performances=recent_performances,
                           avg_score=round(avg_score, 2),
                           weekly_score=round(weekly_score, 2),
                           modules_completed=modules_completed,
                           attendance_percentage=round(attendance_percentage, 1),
                           present_days=present_days,
                           total_days=total_days,
                           recent_attendance=recent_attendance,
                           pending_leaves=pending_leaves,
                           approved_leaves=approved_leaves,
                           recent_leaves=recent_leaves)


# ==================== ATTENDANCE MODULE ====================
@main.route('/mark-attendance', methods=['GET', 'POST'])
@login_required
def mark_attendance():
    if current_user.role != 'student':
        return redirect(url_for('main.admin_dashboard'))

    today = date.today()

    existing_attendance = Attendance.query.filter_by(
        student_id=current_user.id,
        date=today
    ).first()

    if existing_attendance:
        flash('You have already marked attendance for today!', 'warning')
        return redirect(url_for('main.student_dashboard'))

    if request.method == 'POST':
        check_in_time = datetime.now(timezone.utc).time()
        status = request.form.get('status')

        check_out_time_str = request.form.get('check_out_time')
        check_out_time = None
        if check_out_time_str:
            check_out_time = datetime.strptime(check_out_time_str, '%H:%M').time()

        attendance = Attendance(
            student_id=current_user.id,
            date=today,
            status=status,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            remarks=request.form.get('remarks', '')
        )

        db.session.add(attendance)
        db.session.commit()

        flash(f'Attendance marked as {status} for today!', 'success')
        return redirect(url_for('main.student_dashboard'))

    return render_template('mark_attendance.html', now=datetime.now(timezone.utc))


@main.route('/update-checkout', methods=['POST'])
@login_required
def update_checkout():
    today = date.today()

    attendance = Attendance.query.filter_by(
        student_id=current_user.id,
        date=today
    ).first()

    if attendance:
        if attendance.check_out_time:
            flash('You have already checked out for today!', 'warning')
        else:
            attendance.check_out_time = datetime.now(timezone.utc).time()
            db.session.commit()
            flash('Check-out time updated successfully!', 'success')
    else:
        flash('No attendance record found for today! Please mark attendance first.', 'danger')

    return redirect(url_for('main.student_dashboard'))


@main.route('/attendance-history')
@login_required
def attendance_history():
    if current_user.role != 'student':
        return redirect(url_for('main.admin_dashboard'))

    attendances = Attendance.query.filter_by(student_id=current_user.id) \
        .order_by(Attendance.date.desc()).all()

    total_present = Attendance.query.filter_by(student_id=current_user.id, status='Present').count()
    total_absent = Attendance.query.filter_by(student_id=current_user.id, status='Absent').count()
    total_late = Attendance.query.filter_by(student_id=current_user.id, status='Late').count()
    total_attendance = total_present + total_absent + total_late

    attendance_rate = (total_present / total_attendance * 100) if total_attendance > 0 else 0

    return render_template('attendance_history.html',
                           attendances=attendances,
                           total_present=total_present,
                           total_absent=total_absent,
                           total_late=total_late,
                           attendance_rate=round(attendance_rate, 1))


# ==================== LEAVE MANAGEMENT ====================
@main.route('/apply-leave', methods=['GET', 'POST'])
@login_required
def apply_leave():
    if current_user.role != 'student':
        return redirect(url_for('main.admin_dashboard'))

    if request.method == 'POST':
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()

        if start_date < date.today():
            flash('Start date cannot be in the past!', 'danger')
            return render_template('apply_leave.html')

        if end_date < start_date:
            flash('End date must be after start date!', 'danger')
            return render_template('apply_leave.html')

        leave = Leave(
            student_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            leave_type=request.form.get('leave_type'),
            reason=request.form.get('reason'),
            status='Pending'
        )

        db.session.add(leave)
        db.session.commit()

        flash('Leave application submitted successfully!', 'success')
        return redirect(url_for('main.student_dashboard'))

    return render_template('apply_leave.html')


@main.route('/leave-status')
@login_required
def leave_status():
    if current_user.role != 'student':
        return redirect(url_for('main.admin_dashboard'))

    leaves = Leave.query.filter_by(student_id=current_user.id) \
        .order_by(Leave.applied_on.desc()).all()

    return render_template('leave_status.html', leaves=leaves)


# ==================== ADMIN ATTENDANCE MANAGEMENT ====================
@main.route('/admin/attendance')
@login_required
def admin_attendance():
    if current_user.role != 'admin':
        return redirect(url_for('main.student_dashboard'))

    today = date.today()
    students = User.query.filter_by(role='student').all()

    attendance_data = []
    for student in students:
        attendance = Attendance.query.filter_by(
            student_id=student.id,
            date=today
        ).first()

        attendance_data.append({
            'student': student,
            'attendance': attendance
        })

    total_students = len(students)
    present_today = Attendance.query.filter_by(date=today, status='Present').count()
    absent_today = Attendance.query.filter_by(date=today, status='Absent').count()
    late_today = Attendance.query.filter_by(date=today, status='Late').count()

    return render_template('admin_attendance.html',
                           attendance_data=attendance_data,
                           total_students=total_students,
                           present_today=present_today,
                           absent_today=absent_today,
                           late_today=late_today,
                           today=today)


@main.route('/admin/mark-attendance/<int:student_id>', methods=['POST'])
@login_required
def admin_mark_attendance(student_id):
    if current_user.role != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    today = date.today()
    status = request.form.get('status')

    attendance = Attendance.query.filter_by(
        student_id=student_id,
        date=today
    ).first()

    student = User.query.get(student_id)

    if attendance:
        attendance.status = status
        attendance.check_in_time = datetime.now(timezone.utc).time()
        flash(f'Attendance updated for {student.username} to {status}!', 'success')
    else:
        attendance = Attendance(
            student_id=student_id,
            date=today,
            status=status,
            check_in_time=datetime.now(timezone.utc).time()
        )
        db.session.add(attendance)
        flash(f'Attendance marked as {status} for {student.username}!', 'success')

    db.session.commit()
    return redirect(url_for('main.admin_attendance'))


@main.route('/admin/attendance-report')
@login_required
def admin_attendance_report():
    if current_user.role != 'admin':
        return redirect(url_for('main.student_dashboard'))

    students = User.query.filter_by(role='student').all()

    report_data = []
    for student in students:
        total_present = Attendance.query.filter_by(student_id=student.id, status='Present').count()
        total_absent = Attendance.query.filter_by(student_id=student.id, status='Absent').count()
        total_late = Attendance.query.filter_by(student_id=student.id, status='Late').count()
        total = total_present + total_absent + total_late
        percentage = (total_present / total * 100) if total > 0 else 0

        report_data.append({
            'student': student,
            'present': total_present,
            'absent': total_absent,
            'late': total_late,
            'percentage': round(percentage, 1)
        })

    return render_template('admin_attendance_report.html', report_data=report_data)


# ==================== ADMIN LEAVE MANAGEMENT ====================
@main.route('/admin/leaves')
@login_required
def admin_leaves():
    if current_user.role != 'admin':
        return redirect(url_for('main.student_dashboard'))

    pending_leaves = db.session.query(Leave, User).join(User, Leave.student_id == User.id) \
        .filter(Leave.status == 'Pending') \
        .order_by(Leave.applied_on.desc()).all()

    approved_leaves = db.session.query(Leave, User).join(User, Leave.student_id == User.id) \
        .filter(Leave.status == 'Approved') \
        .order_by(Leave.applied_on.desc()).limit(20).all()

    rejected_leaves = db.session.query(Leave, User).join(User, Leave.student_id == User.id) \
        .filter(Leave.status == 'Rejected') \
        .order_by(Leave.applied_on.desc()).limit(20).all()

    return render_template('admin_leaves.html',
                           pending_leaves=pending_leaves,
                           approved_leaves=approved_leaves,
                           rejected_leaves=rejected_leaves)


@main.route('/admin/process-leave/<int:leave_id>', methods=['POST'])
@login_required
def process_leave(leave_id):
    if current_user.role != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.student_dashboard'))

    leave = Leave.query.get_or_404(leave_id)
    action = request.form.get('action')
    remarks = request.form.get('remarks', '')

    if not action:
        flash('No action selected!', 'danger')
        return redirect(url_for('main.admin_leaves'))

    if action == 'approve':
        leave.status = 'Approved'
        flash(f'✅ Leave application approved for Student ID: {leave.student_id}', 'success')
    elif action == 'reject':
        leave.status = 'Rejected'
        flash(f'❌ Leave application rejected for Student ID: {leave.student_id}', 'warning')
    else:
        flash('Invalid action!', 'danger')
        return redirect(url_for('main.admin_leaves'))

    leave.admin_remarks = remarks
    leave.reviewed_on = datetime.now(timezone.utc)
    leave.reviewed_by = current_user.username

    db.session.commit()

    return redirect(url_for('main.admin_leaves'))


# ==================== MODULE AND QUIZ ROUTES ====================
@main.route('/modules')
@login_required
def modules():
    if current_user.role != 'student':
        return redirect(url_for('main.admin_dashboard'))

    all_modules = Module.query.all()

    completed_modules = db.session.query(Performance.module_id) \
        .filter_by(student_id=current_user.id).all()
    completed_ids = [m[0] for m in completed_modules]

    return render_template('modules.html',
                           modules=all_modules,
                           completed_ids=completed_ids)


@main.route('/take-quiz/<int:module_id>', methods=['GET', 'POST'])
@login_required
def take_quiz(module_id):
    if current_user.role != 'student':
        return redirect(url_for('main.admin_dashboard'))

    module = Module.query.get_or_404(module_id)
    quizzes = Quiz.query.filter_by(module_id=module_id).all()

    if not quizzes:
        flash('No quiz questions available for this module yet!', 'warning')
        return redirect(url_for('main.modules'))

    if request.method == 'POST':
        score = 0
        total_points = 0

        for quiz in quizzes:
            answer = request.form.get(f'question_{quiz.id}')
            total_points += quiz.points
            if answer and answer.upper() == quiz.correct_answer:
                score += quiz.points

        percentage_score = (score / total_points) * 100 if total_points > 0 else 0

        current_week = datetime.now(timezone.utc).isocalendar()[1]
        performance = Performance(
            student_id=current_user.id,
            module_id=module_id,
            score=percentage_score,
            time_spent_minutes=10,
            week_number=current_week,
            month_number=datetime.now(timezone.utc).month,
            year=datetime.now(timezone.utc).year
        )
        db.session.add(performance)
        db.session.commit()

        flash(f'Quiz completed! Your score: {percentage_score:.2f}%', 'success')
        return redirect(url_for('main.student_dashboard'))

    return render_template('quiz.html', module=module, quizzes=quizzes)


# ==================== ADMIN DASHBOARD ====================
@main.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.student_dashboard'))

    students = User.query.filter_by(role='student').all()
    modules = Module.query.all()  # ADDED
    total_students = User.query.filter_by(role='student').count()
    total_modules = Module.query.count()
    total_attempts = Performance.query.count()

    today = date.today()
    present_today = Attendance.query.filter_by(date=today, status='Present').count()
    absent_today = Attendance.query.filter_by(date=today, status='Absent').count()

    pending_leaves = Leave.query.filter_by(status='Pending').count()

    top_performers = db.session.query(
        User.username,
        func.avg(Performance.score).label('avg_score')
    ).join(Performance).filter(User.role == 'student') \
        .group_by(User.id).order_by(func.avg(Performance.score).desc()).limit(5).all()

    return render_template('admin_dashboard.html',
                           students=students,
                           modules=modules,  # ADDED
                           total_students=total_students,
                           total_modules=total_modules,
                           total_attempts=total_attempts,
                           present_today=present_today,
                           absent_today=absent_today,
                           pending_leaves=pending_leaves,
                           top_performers=top_performers)


# ==================== ADD MODULE ====================
@main.route('/add-module', methods=['GET', 'POST'])
@login_required
def add_module():
    if current_user.role != 'admin':
        return redirect(url_for('main.student_dashboard'))

    if request.method == 'POST':
        module_name = request.form.get('module_name')
        description = request.form.get('description')
        difficulty = request.form.get('difficulty')
        duration_minutes = request.form.get('duration_minutes')

        if not module_name or not duration_minutes:
            flash('Module name and duration are required!', 'danger')
            return render_template('add_module.html')

        module = Module(
            module_name=module_name,
            description=description,
            difficulty=difficulty,
            duration_minutes=int(duration_minutes)
        )
        db.session.add(module)
        db.session.commit()

        flash(f'Module "{module_name}" added successfully!', 'success')
        return redirect(url_for('main.admin_dashboard'))

    return render_template('add_module.html')


# ==================== DELETE MODULE ====================
@main.route('/admin/delete-module/<int:module_id>', methods=['POST'])
@login_required
def delete_module(module_id):
    if current_user.role != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    module = Module.query.get_or_404(module_id)
    module_name = module.module_name

    # Check if there are any performances linked to this module
    performance_count = Performance.query.filter_by(module_id=module_id).count()

    if performance_count > 0:
        flash(
            f'Cannot delete "{module_name}" because {performance_count} student(s) have taken quizzes for this module!',
            'danger')
        return redirect(url_for('main.admin_dashboard'))

    # Delete associated quizzes first
    Quiz.query.filter_by(module_id=module_id).delete()

    # Delete the module
    db.session.delete(module)
    db.session.commit()

    flash(f'Module "{module_name}" deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))


# ==================== API ROUTES FOR POWER BI ====================
@main.route('/api/performance-data')
@login_required
def performance_data():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    performances = db.session.query(
        User.username.label('student_name'),
        Module.module_name,
        Performance.score,
        Performance.completed_at,
        Performance.week_number,
        Performance.month_number,
        Performance.year
    ).join(User).join(Module).all()

    data = []
    for perf in performances:
        data.append({
            'student_name': perf.student_name,
            'module_name': perf.module_name,
            'score': perf.score,
            'completed_date': perf.completed_at.strftime('%Y-%m-%d') if perf.completed_at else None,
            'week_number': perf.week_number,
            'month_number': perf.month_number,
            'year': perf.year
        })

    return jsonify(data)


@main.route('/api/attendance-data')
@login_required
def attendance_data():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    attendances = db.session.query(
        User.username.label('student_name'),
        Attendance.date,
        Attendance.status,
        Attendance.check_in_time
    ).join(User).all()

    data = []
    for att in attendances:
        data.append({
            'student_name': att.student_name,
            'date': att.date.strftime('%Y-%m-%d') if att.date else None,
            'status': att.status,
            'check_in_time': str(att.check_in_time) if att.check_in_time else None
        })

    return jsonify(data)