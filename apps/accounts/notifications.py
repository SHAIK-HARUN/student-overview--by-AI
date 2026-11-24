"""
Automated Feedback & Notification Engine
Generates AI-explainable feedback and dispatches notifications to parents & class teachers.
"""
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime
from django.conf import settings


def generate_feedback(prediction_obj):
    """
    Generate detailed, explainable AI feedback for a student prediction.
    Returns a dict with structured feedback.
    """
    math = int(prediction_obj.math_score or 0)
    reading = int(prediction_obj.reading_score or 0)
    writing = int(prediction_obj.writing_score or 0)
    avg_score = (math + reading + writing) / 3
    pred = prediction_obj.prediction
    has_internship = str(prediction_obj.internships).lower() not in ['none', 'no', '0', '']
    tasks_on_time = str(getattr(prediction_obj, 'solving_tasks_by_time', '')).lower() in ['yes', 'true', '1', 'on time']
    submitted_on_date = str(getattr(prediction_obj, 'taks_submitted_on_date', getattr(prediction_obj, 'tasks_submitted_on_date', ''))).lower() in ['yes', 'true', '1', 'on time']
    test_prep = str(prediction_obj.test_preparation_course).lower() in ['completed', 'yes', 'true']

    # Strength analysis
    strengths = []
    improvements = []
    recommendations = []

    if math >= 75:
        strengths.append("Strong mathematical aptitude")
    elif math >= 50:
        improvements.append("Mathematics needs moderate improvement (score: {})".format(math))
        recommendations.append("Practice 30 minutes of math problems daily using Khan Academy or similar platforms.")
    else:
        improvements.append("Mathematics is a critical concern (score: {})".format(math))
        recommendations.append("Seek immediate tutoring support for mathematics fundamentals.")

    if reading >= 75:
        strengths.append("Excellent reading comprehension skills")
    elif reading >= 50:
        improvements.append("Reading comprehension needs attention (score: {})".format(reading))
        recommendations.append("Read academic articles and summarize them daily to improve comprehension.")
    else:
        improvements.append("Reading proficiency is below expected level (score: {})".format(reading))
        recommendations.append("Start a daily reading habit with graded readers to build comprehension.")

    if writing >= 75:
        strengths.append("Strong writing and communication skills")
    elif writing >= 50:
        improvements.append("Writing skills require improvement (score: {})".format(writing))
        recommendations.append("Practice essay writing with peer review sessions weekly.")
    else:
        improvements.append("Writing skills need significant development (score: {})".format(writing))
        recommendations.append("Enroll in a structured writing workshop or online course.")

    if has_internship:
        strengths.append("Practical industry experience through internships")
    else:
        recommendations.append("Pursue internship or project opportunities to gain practical exposure.")

    if tasks_on_time:
        strengths.append("Excellent time management — solves tasks on schedule")
    else:
        improvements.append("Task completion timeliness needs improvement")
        recommendations.append("Use time-blocking and task management tools (e.g., Trello, Notion) to plan submissions.")

    if submitted_on_date:
        strengths.append("Consistent in submitting assignments on due dates")
    else:
        improvements.append("Assignment submission punctuality is an issue")
        recommendations.append("Set reminders 2 days before deadlines and break assignments into smaller milestones.")

    if test_prep:
        strengths.append("Completed test preparation course — well prepared")
    else:
        improvements.append("Test preparation course not completed")
        recommendations.append("Complete available test preparation resources before upcoming assessments.")

    # Determine performance band
    if pred == 'Excellent' or avg_score >= 80:
        grade_band = "Outstanding"
        emoji = "🌟"
        summary = (
            "This student demonstrates outstanding academic performance with strong scores across "
            "all subjects. Their dedication, time management, and academic discipline are commendable."
        )
    elif avg_score >= 65:
        grade_band = "Good"
        emoji = "✅"
        summary = (
            "This student shows good academic performance with room for growth in specific areas. "
            "With focused effort, they can achieve excellent results."
        )
    elif avg_score >= 50 or pred == 'Average':
        grade_band = "Average"
        emoji = "⚠️"
        summary = (
            "This student's performance is at an average level. Targeted intervention and additional "
            "support in weak areas can significantly improve their academic standing."
        )
    else:
        grade_band = "Needs Attention"
        emoji = "🔴"
        summary = (
            "This student's performance requires immediate attention and support. We strongly recommend "
            "coordinated efforts between parents, the class teacher, and the student to address the gaps."
        )

    return {
        'student_id': prediction_obj.fid,
        'predicted_profile': pred,
        'grade_band': grade_band,
        'emoji': emoji,
        'average_score': round(avg_score, 1),
        'math_score': math,
        'reading_score': reading,
        'writing_score': writing,
        'summary': summary,
        'strengths': strengths,
        'improvements': improvements,
        'recommendations': recommendations,
        'generated_at': datetime.now().strftime('%d %b %Y, %I:%M %p'),
        'parental_level_of_education': prediction_obj.parental_level_of_education,
        'test_preparation_course': prediction_obj.test_preparation_course,
    }


def compose_message(feedback, recipient_type, student_obj=None):
    """Compose a personalized message for parent or teacher."""
    sid = feedback['student_id']
    name = (
        getattr(student_obj, 'student_name', None) or
        getattr(student_obj, 'full_name', None) or
        sid
    )
    band = feedback['grade_band']
    emoji = feedback['emoji']
    avg = feedback['average_score']
    pred = feedback['predicted_profile']
    summary = feedback['summary']
    strengths_txt = "\n  • " + "\n  • ".join(feedback['strengths']) if feedback['strengths'] else "  • To be assessed"
    improvements_txt = "\n  • " + "\n  • ".join(feedback['improvements']) if feedback['improvements'] else "  • None identified"
    recommendations_txt = "\n  1. " + "\n  2. ".join(feedback['recommendations']) if feedback['recommendations'] else "  1. Continue current good practices"
    generated = feedback['generated_at']

    if recipient_type == 'parent':
        subject = f"[AI Report] {name}'s Academic Performance — {band} {emoji}"
        message = f"""
Dear Parent / Guardian of {name},

We are reaching out to share the AI-powered academic performance report generated by the Student Profile Intelligence System.

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 STUDENT PERFORMANCE REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━
Student ID     : {sid}
Full Name      : {name}
AI Profile     : {pred} {emoji}
Performance    : {band}
Average Score  : {avg}%
  • Mathematics   : {feedback['math_score']}
  • Reading       : {feedback['reading_score']}
  • Writing       : {feedback['writing_score']}

📋 SUMMARY:
{summary}

✅ STRENGTHS:{strengths_txt}

⚠️ AREAS FOR IMPROVEMENT:{improvements_txt}

💡 RECOMMENDATIONS:
{recommendations_txt}

━━━━━━━━━━━━━━━━━━━━━━━━━━
Report generated on: {generated}
System: Student Profile AI Portal (XAI System)
━━━━━━━━━━━━━━━━━━━━━━━━━━

We encourage your active involvement in supporting your child's academic journey.
Please feel free to contact the class teacher for further guidance.

Warm regards,
Student Academic Intelligence System
        """.strip()
    else:
        subject = f"[AI Report] Student {name} — {band} {emoji} Performance Alert"
        message = f"""
Dear Class Teacher,

This is an automated academic performance notification from the Student Profile AI System.

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 STUDENT ANALYSIS REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━
Student ID     : {sid}
Full Name      : {name}
AI Profile     : {pred} {emoji}
Performance    : {band}
Average Score  : {avg}%
  • Mathematics   : {feedback['math_score']}
  • Reading       : {feedback['reading_score']}
  • Writing       : {feedback['writing_score']}

Background:
  • Parental Education : {feedback['parental_level_of_education']}
  • Test Prep Done     : {feedback['test_preparation_course']}

📋 AI ANALYSIS SUMMARY:
{summary}

✅ STUDENT STRENGTHS:{strengths_txt}

⚠️ AREAS NEEDING CLASSROOM ATTENTION:{improvements_txt}

💡 SUGGESTED INTERVENTIONS:
{recommendations_txt}

━━━━━━━━━━━━━━━━━━━━━━━━━━
Report generated on: {generated}
System: Student Profile AI Portal (XAI System)
━━━━━━━━━━━━━━━━━━━━━━━━━━

Please review this student's progress and consider additional support strategies as needed.

Regards,
Student Academic Intelligence System
        """.strip()

    return subject, message


def clean_phone_number(phone_raw):
    """Normalize phone number to international digits format (e.g., 919182257621)"""
    if not phone_raw:
        return ""
    digits = re.sub(r'\D', '', str(phone_raw))
    # If 10 digits given, prepend India country code 91
    if len(digits) == 10:
        digits = "91" + digits
    return digits


def compose_whatsapp_text(feedback, recipient_type, student_obj=None):
    """Compose concise, emoji-rich WhatsApp message for mobile viewing."""
    sid = feedback['student_id']
    name = (
        getattr(student_obj, 'student_name', None) or
        getattr(student_obj, 'full_name', None) or
        sid
    )
    band = feedback['grade_band']
    emoji = feedback['emoji']
    avg = feedback['average_score']
    pred = feedback.get('prediction_label') or feedback.get('predicted_profile', 'Average')
    strengths_txt = ", ".join(feedback['strengths'][:2]) if feedback['strengths'] else "Good academic effort"
    rec_txt = feedback['recommendations'][0] if feedback['recommendations'] else "Maintain current study consistency"
    college_num = getattr(settings, 'COLLEGE_WHATSAPP_NUMBER', '+919182257621')

    if recipient_type == 'parent':
        msg = (
            f"🎓 *COLLEGE ACADEMIC REPORT*\n"
            f"From College Desk: {college_num}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"Dear Parent/Guardian,\n"
            f"Here is the AI Academic Report for *{name}* (Student ID: {sid}):\n\n"
            f"⭐ *Performance Profile:* {pred} {emoji} ({band})\n"
            f"📊 *Average Score:* {avg}%\n"
            f"  • Math: {feedback['math_score']}\n"
            f"  • Reading: {feedback['reading_score']}\n"
            f"  • Writing: {feedback['writing_score']}\n\n"
            f"✅ *Key Strengths:* {strengths_txt}\n"
            f"💡 *Recommended Action:* {rec_txt}\n\n"
            f"🏫 *Teacher & Student Profile Intelligence System (XAI)*"
        )
    else:
        msg = (
            f"👨‍🏫 *STUDENT ACADEMIC ALERT*\n"
            f"From College Admin: {college_num}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"Dear Class Teacher,\n"
            f"Academic assessment generated for *{name}* (Student ID: {sid}):\n\n"
            f"⭐ *AI Profile:* {pred} {emoji} ({band})\n"
            f"📊 *Score Average:* {avg}% (M:{feedback['math_score']} R:{feedback['reading_score']} W:{feedback['writing_score']})\n"
            f"🎯 *Intervention:* {rec_txt}\n\n"
            f"🏫 *Teacher Academic Intelligence System*"
        )
    return msg


def send_whatsapp_message(to_phone, message_text):
    """
    Sends WhatsApp message via direct Internet HTTP API (if configured)
    and constructs a direct one-click WhatsApp web/app link.
    Returns: (status, detail_message, wa_link)
    """
    clean_num = clean_phone_number(to_phone)
    if not clean_num:
        return 'failed', 'Invalid phone number format', ''

    encoded_text = urllib.parse.quote(message_text)
    # Direct universal WhatsApp link
    wa_link = f"https://api.whatsapp.com/send?phone={clean_num}&text={encoded_text}"

    api_url = getattr(settings, 'WHATSAPP_API_URL', '')
    api_token = getattr(settings, 'WHATSAPP_API_TOKEN', '')

    if api_url:
        try:
            req_data = json.dumps({
                "to": clean_num,
                "message": message_text,
                "sender": getattr(settings, 'COLLEGE_WHATSAPP_NUMBER', '+919182257621')
            }).encode('utf-8')

            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'StudentPortal-XAI/1.0'
            }
            if api_token:
                headers['Authorization'] = f"Bearer {api_token}"

            req = urllib.request.Request(api_url, data=req_data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status in [200, 201, 202]:
                    return 'sent', f"WhatsApp delivered via Internet API to +{clean_num}", wa_link
        except Exception as e:
            return 'failed', f"WhatsApp API delivery error ({str(e)[:70]})", wa_link

    # Fallback to direct wa.me automated link dispatch
    return 'sent', f"WhatsApp message prepared for +{clean_num} from {getattr(settings, 'COLLEGE_WHATSAPP_NUMBER', '+919182257621')}", wa_link


def send_notification(prediction_obj, student_obj=None):
    """
    Main notification dispatch function.
    Generates feedback, composes messages, and sends to parent + teacher.
    Returns a summary dict of what was sent.
    """
    from apps.accounts.models import NotificationLog

    feedback = generate_feedback(prediction_obj)
    logs = []
    summary_lines = []

    # Determine contacts
    contacts = []

    # 1. Resolve Parent Contact (from student_obj or prediction_obj)
    parent_email = getattr(student_obj, 'parent_email', '') or getattr(prediction_obj, 'parent_email', '')
    parent_phone = getattr(student_obj, 'parent_phone', '') or getattr(prediction_obj, 'parent_phone', '')
    parent_name = getattr(student_obj, 'parent_name', '') or getattr(prediction_obj, 'parent_name', '') or 'Parent / Guardian'

    if parent_email or parent_phone:
        contacts.append({
            'type': 'parent',
            'name': parent_name,
            'email': parent_email,
            'phone': parent_phone,
        })

    # 2. Resolve Class Teacher Contact
    teacher = getattr(student_obj, 'teacher', None) or getattr(prediction_obj, 'teacher', None)
    if teacher:
        if getattr(teacher, 'email', None) or getattr(teacher, 'phoneno', None):
            contacts.append({
                'type': 'teacher',
                'name': teacher.full_name or teacher.username or 'Class Teacher',
                'email': teacher.email,
                'phone': teacher.phoneno,
            })
    else:
        # Check direct fields if any
        t_email = getattr(student_obj, 'teacher_email', '')
        t_phone = getattr(student_obj, 'teacher_phone', '')
        t_name = getattr(student_obj, 'teacher_name', '') or 'Class Teacher'
        if t_email or t_phone:
            contacts.append({
                'type': 'teacher',
                'name': t_name,
                'email': t_email,
                'phone': t_phone,
            })

    if not contacts:
        summary_lines.append("⚠️ No parent contact info available. Please add parent phone/email.")
        return feedback, summary_lines

    for contact in contacts:
        subject, message = compose_message(feedback, contact['type'], student_obj)

        # 1. EMAIL DISPATCH
        if contact['email']:
            status_email = 'simulated'
            sent_detail_email = []
            from_addr = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or settings.EMAIL_HOST_USER or 'shaikashfaq911@gmail.com'
            try:
                from django.core.mail import send_mail
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_addr,
                    recipient_list=[contact['email']],
                    fail_silently=False,
                )
                status_email = 'sent'
                sent_detail_email.append(f"Email sent via {from_addr} → {contact['email']}")
            except Exception as e:
                status_email = 'failed'
                err_msg = str(e)
                sent_detail_email.append(f"Email error ({err_msg[:90]})")
                print(f"[EMAIL ERROR] Failed to send to {contact['email']}: {err_msg}")

            NotificationLog.objects.create(
                prediction=prediction_obj,
                recipient_type=contact['type'],
                channel='email',
                recipient_name=contact['name'],
                recipient_contact=contact['email'],
                subject=subject,
                message=message,
                status=status_email,
            )
            emoji_email = "✅" if status_email == 'sent' else ("❌" if status_email == 'failed' else "📧")
            summary_lines.append(
                f"{emoji_email} Email to {contact['type'].title()} ({contact['name']}): {', '.join(sent_detail_email)}"
            )

        # 2. WHATSAPP DISPATCH (From College WhatsApp: +91 9182257621)
        if contact['phone']:
            wa_text = compose_whatsapp_text(feedback, contact['type'], student_obj)
            wa_status, wa_detail, wa_link = send_whatsapp_message(contact['phone'], wa_text)

            NotificationLog.objects.create(
                prediction=prediction_obj,
                recipient_type=contact['type'],
                channel='whatsapp',
                recipient_name=contact['name'],
                recipient_contact=contact['phone'],
                subject=f"WhatsApp Report from College ({getattr(settings, 'COLLEGE_WHATSAPP_NUMBER', '+919182257621')})",
                message=wa_text,
                whatsapp_link=wa_link,
                status=wa_status,
            )
            summary_lines.append(
                f"💬 WhatsApp to {contact['type'].title()} ({contact['phone']}): {wa_detail}"
            )

    return feedback, summary_lines
