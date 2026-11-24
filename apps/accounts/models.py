from django.db import models


from django.db import models


class TeacherProfile(models.Model):
    """Teacher registration model with department, subject, phone and email"""
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    full_name = models.CharField(max_length=100, blank=True)
    phoneno = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True, default="Computer Science")
    designation = models.CharField(max_length=100, blank=True, default="Class Teacher")
    gender = models.CharField(max_length=10, choices=[
        ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')
    ], default='Male')
    country = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name or self.username} ({self.designation})"

    class Meta:
        verbose_name = "Teacher Profile"
        ordering = ['-created_at']


class StudentRecord(models.Model):
    """Student details added by the Class Teacher, including parent contact info"""
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE,
                                related_name='students', null=True, blank=True)
    fid = models.CharField(max_length=300, verbose_name="Student ID / Fid")
    student_name = models.CharField(max_length=100, blank=True, verbose_name="Student Name")
    age = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    lunch = models.CharField(max_length=50)
    parental_level_of_education = models.CharField(max_length=100)
    degree_t = models.CharField(max_length=100, blank=True, verbose_name="Degree")
    race_ethnicity = models.CharField(max_length=50)
    test_preparation_course = models.CharField(max_length=50)
    math_score = models.IntegerField(default=0)
    reading_score = models.IntegerField(default=0)
    writing_score = models.IntegerField(default=0)
    internships = models.CharField(max_length=50, default='0', verbose_name="Internships")
    solving_tasks_by_time = models.CharField(max_length=50, verbose_name="Solving tasks by time")
    taks_submitted_on_date = models.CharField(max_length=50, verbose_name="Task submitted on date")

    # Parent Contact Details (where predictions and reports are sent)
    parent_name = models.CharField(max_length=100, blank=True, verbose_name="Parent Name")
    parent_phone = models.CharField(max_length=20, blank=True, verbose_name="Parent Phone")
    parent_email = models.EmailField(max_length=100, blank=True, verbose_name="Parent Email")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fid} - {self.student_name or 'Student'}"

    @property
    def average_score(self):
        try:
            return round((int(self.math_score or 0) + int(self.reading_score or 0) + int(self.writing_score or 0)) / 3.0, 1)
        except Exception:
            return 0

    class Meta:
        verbose_name = "Student Record"
        ordering = ['-created_at']


class StudentPrediction(models.Model):
    """Stores each prediction run for a student"""
    PREDICTION_CHOICES = [
        ('Excellent', 'Excellent'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor'),
    ]

    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE,
                                related_name='predictions', null=True, blank=True)
    student = models.ForeignKey(StudentRecord, on_delete=models.CASCADE,
                                related_name='predictions', null=True, blank=True)
    fid = models.CharField(max_length=300, verbose_name="Student ID")
    student_name = models.CharField(max_length=100, blank=True)
    age = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    lunch = models.CharField(max_length=50)
    parental_level_of_education = models.CharField(max_length=100)
    degree_t = models.CharField(max_length=100, blank=True)
    race_ethnicity = models.CharField(max_length=50)
    test_preparation_course = models.CharField(max_length=50)
    math_score = models.IntegerField(default=0)
    reading_score = models.IntegerField(default=0)
    writing_score = models.IntegerField(default=0)
    internships = models.CharField(max_length=50, default='0')
    solving_tasks_by_time = models.CharField(max_length=50)
    taks_submitted_on_date = models.CharField(max_length=50)

    # Parent Contact
    parent_name = models.CharField(max_length=100, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    parent_email = models.EmailField(max_length=100, blank=True)

    prediction = models.CharField(max_length=20, choices=PREDICTION_CHOICES, blank=True)
    feedback_text = models.TextField(blank=True)
    notification_sent = models.BooleanField(default=False)
    notification_log = models.TextField(blank=True)
    predicted_at = models.DateTimeField(auto_now_add=True)

    @property
    def average_score(self):
        try:
            return round((int(self.math_score or 0) + int(self.reading_score or 0) + int(self.writing_score or 0)) / 3.0, 1)
        except Exception:
            return 0

    def __str__(self):
        return f"{self.fid} → {self.prediction}"

    class Meta:
        verbose_name = "Student Prediction"
        ordering = ['-predicted_at']


class AlgorithmAccuracy(models.Model):
    """Accuracy of each ML algorithm after training"""
    name = models.CharField(max_length=100)
    accuracy = models.FloatField(default=0.0)
    precision_score = models.FloatField(default=0.0)
    recall_score = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)
    execution_time = models.FloatField(default=0.0)  # seconds
    trained_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.accuracy:.1f}%"

    class Meta:
        ordering = ['-accuracy']


class DetectionRatio(models.Model):
    """Ratio of predicted categories"""
    label = models.CharField(max_length=50)
    count = models.IntegerField(default=0)
    ratio = models.FloatField(default=0.0)
    computed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label}: {self.ratio:.1f}%"

    class Meta:
        ordering = ['-count']


class NotificationLog(models.Model):
    """Log of all notifications sent to parents/teachers"""
    RECIPIENT_CHOICES = [
        ('parent', 'Parent'),
        ('teacher', 'Class Teacher'),
        ('both', 'Both'),
    ]
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
    ]
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('simulated', 'Simulated'),
        ('failed', 'Failed'),
    ]

    prediction = models.ForeignKey(StudentPrediction, on_delete=models.CASCADE,
                                   related_name='notifications')
    recipient_type = models.CharField(max_length=10, choices=RECIPIENT_CHOICES)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='email')
    recipient_name = models.CharField(max_length=100, blank=True)
    recipient_contact = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    whatsapp_link = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='simulated')
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.status}] {self.recipient_type} → {self.prediction.fid}"

    class Meta:
        ordering = ['-sent_at']
