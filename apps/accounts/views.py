from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import TeacherProfile, StudentRecord, StudentPrediction, NotificationLog
from .notifications import send_notification, generate_feedback
from .ml_engine import predict_student


# ──────────────────────────────────────────────────
# Landing Page
# ──────────────────────────────────────────────────
def index(request):
    return render(request, 'accounts/index.html')


# ──────────────────────────────────────────────────
# Teacher Authentication
# ──────────────────────────────────────────────────
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/register.html')

        if not username:
            messages.error(request, "Username is required.")
            return render(request, 'accounts/register.html')

        if TeacherProfile.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'accounts/register.html')

        if email and TeacherProfile.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'accounts/register.html')

        teacher = TeacherProfile.objects.create(
            username=username,
            email=email or f"{username}@college.local",
            password=make_password(password),
            full_name=request.POST.get('full_name', ''),
            phoneno=request.POST.get('phoneno', ''),
            department=request.POST.get('department', 'Computer Science'),
            designation=request.POST.get('designation', 'Class Teacher'),
            gender=request.POST.get('gender', 'Male'),
            country=request.POST.get('country', ''),
            state=request.POST.get('state', ''),
            city=request.POST.get('city', ''),
            address=request.POST.get('address', ''),
        )
        messages.success(request, "Teacher account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        try:
            # Allow login using username or phone/email if entered, strictly without requiring email
            from django.db.models import Q
            teacher = TeacherProfile.objects.filter(
                Q(username=identifier) | Q(email=identifier) | Q(phoneno=identifier)
            ).first()
            if teacher and check_password(password, teacher.password):
                request.session['teacher_id'] = teacher.id
                request.session['teacher_name'] = teacher.full_name or teacher.username
                messages.success(request, f"Welcome back, Prof./Teacher {teacher.full_name or teacher.username}!")
                return redirect('teacher_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        except Exception as e:
            messages.error(request, "Error during login. Please try again.")
    return render(request, 'accounts/login.html')


def logout_view(request):
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect('login')


def _get_logged_in_teacher(request):
    teacher_id = request.session.get('teacher_id')
    if not teacher_id:
        return None
    try:
        return TeacherProfile.objects.get(id=teacher_id)
    except TeacherProfile.DoesNotExist:
        return None


# ──────────────────────────────────────────────────
# Teacher Dashboard
# ──────────────────────────────────────────────────
def teacher_dashboard(request):
    teacher = _get_logged_in_teacher(request)
    if not teacher:
        return redirect('login')

    students = StudentRecord.objects.filter(teacher=teacher).order_by('-created_at')
    predictions = StudentPrediction.objects.filter(teacher=teacher).order_by('-predicted_at')[:8]

    total_students = students.count()
    total_predictions = StudentPrediction.objects.filter(teacher=teacher).count()
    excellent_count = StudentPrediction.objects.filter(teacher=teacher, prediction='Excellent').count()
    poor_count = StudentPrediction.objects.filter(teacher=teacher, prediction='Poor').count()

    context = {
        'teacher': teacher,
        'students': students,
        'predictions': predictions,
        'total_students': total_students,
        'total_predictions': total_predictions,
        'excellent_count': excellent_count,
        'poor_count': poor_count,
        'active': 'dashboard',
    }
    return render(request, 'accounts/teacher_dashboard.html', context)


# ──────────────────────────────────────────────────
# Teacher Profile
# ──────────────────────────────────────────────────
def profile_view(request):
    teacher = _get_logged_in_teacher(request)
    if not teacher:
        return redirect('login')
    return render(request, 'accounts/profile.html', {'teacher': teacher, 'active': 'profile'})


def profile_update(request):
    teacher = _get_logged_in_teacher(request)
    if not teacher:
        return redirect('login')

    if request.method == 'POST':
        teacher.full_name = request.POST.get('full_name', teacher.full_name)
        teacher.email = request.POST.get('email', teacher.email)
        teacher.phoneno = request.POST.get('phoneno', teacher.phoneno)
        teacher.department = request.POST.get('department', teacher.department)
        teacher.designation = request.POST.get('designation', teacher.designation)
        teacher.gender = request.POST.get('gender', teacher.gender)
        teacher.country = request.POST.get('country', teacher.country)
        teacher.state = request.POST.get('state', teacher.state)
        teacher.city = request.POST.get('city', teacher.city)
        teacher.address = request.POST.get('address', teacher.address)

        teacher.save()
        messages.success(request, "Teacher profile updated successfully!")
        return redirect('profile_view')

    return render(request, 'accounts/profile_update.html', {'teacher': teacher, 'active': 'profile'})


# ──────────────────────────────────────────────────
# Add Student Details & Predict Result
# ──────────────────────────────────────────────────
def add_student_view(request):
    """
    Class Teacher adds student with full attributes:
    Fid, age, gender, lunch, parental_level_of_education, degree_t,
    race_ethnicity, test_preparation_course, math_score, reading_score,
    writing_score, Internships, solving_tasks_by_time, taks_submitted_on_date,
    and Parent contact details.
    """
    teacher = _get_logged_in_teacher(request)
    if not teacher:
        return redirect('login')

    if request.method == 'POST':
        fid = request.POST.get('fid', '').strip()
        student_name = request.POST.get('student_name', '').strip()
        age = request.POST.get('age', '21')
        gender = request.POST.get('gender', 'Male')
        lunch = request.POST.get('lunch', 'standard')
        parental_level_of_education = request.POST.get('parental_level_of_education', 'some college')
        degree_t = request.POST.get('degree_t', 'Sci&Tech')
        race_ethnicity = request.POST.get('race_ethnicity', 'group B')
        test_preparation_course = request.POST.get('test_preparation_course', 'completed')
        math_score = int(request.POST.get('math_score', 0) or 0)
        reading_score = int(request.POST.get('reading_score', 0) or 0)
        writing_score = int(request.POST.get('writing_score', 0) or 0)
        internships = request.POST.get('internships', '0')
        solving_tasks_by_time = request.POST.get('solving_tasks_by_time', '1')
        taks_submitted_on_date = request.POST.get('taks_submitted_on_date', '1')

        # Parent contacts
        parent_name = request.POST.get('parent_name', '').strip()
        parent_phone = request.POST.get('parent_phone', '').strip()
        parent_email = request.POST.get('parent_email', '').strip()

        # Create or update student record
        student_rec, _ = StudentRecord.objects.update_or_create(
            teacher=teacher,
            fid=fid,
            defaults={
                'student_name': student_name,
                'age': age,
                'gender': gender,
                'lunch': lunch,
                'parental_level_of_education': parental_level_of_education,
                'degree_t': degree_t,
                'race_ethnicity': race_ethnicity,
                'test_preparation_course': test_preparation_course,
                'math_score': math_score,
                'reading_score': reading_score,
                'writing_score': writing_score,
                'internships': internships,
                'solving_tasks_by_time': solving_tasks_by_time,
                'taks_submitted_on_date': taks_submitted_on_date,
                'parent_name': parent_name,
                'parent_phone': parent_phone,
                'parent_email': parent_email,
            }
        )

        # AI Prediction
        prediction_label, _, _ = predict_student(
            fid=fid,
            math_score=math_score,
            reading_score=reading_score,
            writing_score=writing_score,
        )

        pred_obj = StudentPrediction.objects.create(
            teacher=teacher,
            student=student_rec,
            fid=fid,
            student_name=student_name,
            age=age,
            gender=gender,
            lunch=lunch,
            parental_level_of_education=parental_level_of_education,
            degree_t=degree_t,
            race_ethnicity=race_ethnicity,
            test_preparation_course=test_preparation_course,
            math_score=math_score,
            reading_score=reading_score,
            writing_score=writing_score,
            internships=internships,
            solving_tasks_by_time=solving_tasks_by_time,
            taks_submitted_on_date=taks_submitted_on_date,
            parent_name=parent_name,
            parent_phone=parent_phone,
            parent_email=parent_email,
            prediction=prediction_label,
        )

        # Generate Explainable AI Feedback
        feedback = generate_feedback(pred_obj)
        pred_obj.feedback_text = str(feedback)
        pred_obj.save()

        # Send notifications directly to Parent (Email + WhatsApp)
        fb, notif_summary = send_notification(pred_obj, student_rec)
        pred_obj.notification_sent = True
        pred_obj.notification_log = "\n".join(notif_summary)
        pred_obj.save()

        messages.success(request, f"Student {fid} added! Prediction: {prediction_label}. Notification sent to Parents.")
        return redirect('result_view', pk=pred_obj.pk)

    return render(request, 'accounts/add_student.html', {'teacher': teacher, 'active': 'add_student'})


def student_list_view(request):
    """View all students managed by this class teacher"""
    teacher = _get_logged_in_teacher(request)
    if not teacher:
        return redirect('login')

    students = StudentRecord.objects.filter(teacher=teacher).order_by('-created_at')
    return render(request, 'accounts/student_list.html', {'teacher': teacher, 'students': students, 'active': 'students'})


def result_view(request, pk):
    teacher = _get_logged_in_teacher(request)
    if not teacher:
        return redirect('login')

    pred_obj = get_object_or_404(StudentPrediction, pk=pk, teacher=teacher)
    feedback = generate_feedback(pred_obj)
    notif_logs = NotificationLog.objects.filter(prediction=pred_obj)

    context = {
        'teacher': teacher,
        'pred': pred_obj,
        'feedback': feedback,
        'notif_logs': notif_logs,
        'active': 'students',
    }
    return render(request, 'accounts/result.html', context)


def regenerate_result(request, pk):
    """Re-run prediction and re-notify parents directly"""
    teacher = _get_logged_in_teacher(request)
    if not teacher:
        return redirect('login')

    pred_obj = get_object_or_404(StudentPrediction, pk=pk, teacher=teacher)

    prediction_label, _, _ = predict_student(
        fid=pred_obj.fid,
        math_score=pred_obj.math_score,
        reading_score=pred_obj.reading_score,
        writing_score=pred_obj.writing_score,
    )
    pred_obj.prediction = prediction_label

    feedback = generate_feedback(pred_obj)
    pred_obj.feedback_text = str(feedback)

    # Delete previous notification logs and re-dispatch to parent
    NotificationLog.objects.filter(prediction=pred_obj).delete()
    fb, notif_summary = send_notification(pred_obj, pred_obj.student)
    pred_obj.notification_sent = True
    pred_obj.notification_log = "\n".join(notif_summary)
    pred_obj.save()

    messages.success(request, f"Result regenerated: {prediction_label}. Report re-accumulated and sent to parents!")
    return redirect('result_view', pk=pred_obj.pk)


def prediction_history(request):
    teacher = _get_logged_in_teacher(request)
    if not teacher:
        return redirect('login')

    predictions = StudentPrediction.objects.filter(teacher=teacher).order_by('-predicted_at')
    context = {
        'teacher': teacher,
        'predictions': predictions,
        'active': 'history',
    }
    return render(request, 'accounts/prediction_history.html', context)
