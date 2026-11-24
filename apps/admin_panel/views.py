import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count
from apps.accounts.models import (
    TeacherProfile, StudentRecord, StudentPrediction,
    AlgorithmAccuracy, DetectionRatio, NotificationLog
)
from apps.accounts.ml_engine import train_all_models


ADMIN_USERNAME = 'Admin'
ADMIN_PASSWORD = 'Admin'


def _admin_required(request):
    return request.session.get('admin_logged_in', False)


# ──────────────────────────────────────────────────
# Auth
# ──────────────────────────────────────────────────
def admin_login(request):
    if request.method == 'POST':
        uname = request.POST.get('username', '')
        pwd = request.POST.get('password', '')
        if uname == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            request.session['admin_logged_in'] = True
            messages.success(request, "Welcome, Administrator!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid admin credentials.")
    return render(request, 'admin_panel/admin_login.html')


def admin_logout(request):
    request.session.pop('admin_logged_in', None)
    messages.info(request, "Logged out from admin panel.")
    return redirect('admin_login')


# ──────────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────────
def admin_dashboard(request):
    if not _admin_required(request):
        return redirect('admin_login')

    total_students = StudentRecord.objects.count()
    total_teachers = TeacherProfile.objects.count()
    total_predictions = StudentPrediction.objects.count()
    excellent = StudentPrediction.objects.filter(prediction='Excellent').count()
    poor = StudentPrediction.objects.filter(prediction='Poor').count()
    good = StudentPrediction.objects.filter(prediction='Good').count()
    average = StudentPrediction.objects.filter(prediction='Average').count()
    total_notifications = NotificationLog.objects.count()
    algo_count = AlgorithmAccuracy.objects.count()

    recent_preds = StudentPrediction.objects.select_related('student').order_by('-predicted_at')[:8]

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_predictions': total_predictions,
        'excellent': excellent,
        'poor': poor,
        'good': good,
        'average': average,
        'total_notifications': total_notifications,
        'algo_count': algo_count,
        'recent_preds': recent_preds,
        'active': 'dashboard',
    }
    return render(request, 'admin_panel/admin_dashboard.html', context)


# ──────────────────────────────────────────────────
# Users
# ──────────────────────────────────────────────────
def view_students(request):
    if not _admin_required(request):
        return redirect('admin_login')
    students = StudentRecord.objects.select_related('teacher').order_by('-created_at')
    teachers = TeacherProfile.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/view_students.html', {'students': students, 'teachers': teachers, 'active': 'students'})


def view_predictions(request):
    if not _admin_required(request):
        return redirect('admin_login')
    predictions = StudentPrediction.objects.select_related('student').order_by('-predicted_at')
    return render(request, 'admin_panel/view_predictions.html', {'predictions': predictions, 'active': 'predictions'})


def view_notifications(request):
    if not _admin_required(request):
        return redirect('admin_login')
    logs = NotificationLog.objects.select_related('prediction').order_by('-sent_at')
    return render(request, 'admin_panel/view_notifications.html', {'logs': logs, 'active': 'notifications'})


# ──────────────────────────────────────────────────
# Train Model
# ──────────────────────────────────────────────────
def train_model_view(request):
    if not _admin_required(request):
        return redirect('admin_login')

    results = None
    error = None

    if request.method == 'POST':
        results, error = train_all_models()
        if error:
            messages.error(request, error)
        else:
            # Recompute detection ratios
            DetectionRatio.objects.all().delete()
            total = StudentPrediction.objects.count()
            if total > 0:
                for label in ['Excellent', 'Good', 'Average', 'Poor']:
                    cnt = StudentPrediction.objects.filter(prediction=label).count()
                    if cnt > 0:
                        DetectionRatio.objects.create(
                            label=label,
                            count=cnt,
                            ratio=round((cnt / total) * 100, 2)
                        )
            messages.success(request, f"Training complete! {len(results)} models trained.")

    algo_data = AlgorithmAccuracy.objects.all()
    context = {
        'results': results,
        'error': error,
        'algo_data': algo_data,
        'active': 'train',
    }
    return render(request, 'admin_panel/train_model.html', context)


# ──────────────────────────────────────────────────
# Charts – JSON API endpoints
# ──────────────────────────────────────────────────
def _get_algo_chart_data():
    algos = AlgorithmAccuracy.objects.all()
    return {
        'labels': [a.name for a in algos],
        'accuracy': [a.accuracy for a in algos],
        'precision': [a.precision_score for a in algos],
        'recall': [a.recall_score for a in algos],
        'f1': [a.f1_score for a in algos],
        'execution_time': [a.execution_time for a in algos],
    }


def _get_prediction_dist():
    ratios = DetectionRatio.objects.all()
    if not ratios.exists():
        # Compute on-the-fly
        total = StudentPrediction.objects.count()
        result = {'labels': [], 'counts': [], 'ratios': []}
        if total > 0:
            for label in ['Excellent', 'Good', 'Average', 'Poor']:
                cnt = StudentPrediction.objects.filter(prediction=label).count()
                if cnt > 0:
                    result['labels'].append(label)
                    result['counts'].append(cnt)
                    result['ratios'].append(round((cnt / total) * 100, 2))
        return result
    return {
        'labels': [r.label for r in ratios],
        'counts': [r.count for r in ratios],
        'ratios': [r.ratio for r in ratios],
    }


def admin_charts(request):
    if not _admin_required(request):
        return redirect('admin_login')

    algo_data = _get_algo_chart_data()
    pred_dist = _get_prediction_dist()
    chart_type = request.GET.get('chart', 'bar')

    chart_types = [
        ('bar', 'Bar', 'bar-chart-fill'),
        ('line', 'Line', 'graph-up'),
        ('radar', 'Radar', 'reception-4'),
        ('horizontalbar', 'H-Bar', 'bar-chart-horizontal'),
        ('pie', 'Pie', 'pie-chart-fill'),
        ('doughnut', 'Doughnut', 'circle-half'),
        ('polararea', 'Polar Area', 'vinyl-fill'),
    ]
    algo_table = AlgorithmAccuracy.objects.all()

    context = {
        'algo_data_json': json.dumps(algo_data),
        'pred_dist_json': json.dumps(pred_dist),
        'chart_type': chart_type,
        'chart_types': chart_types,
        'algo_table': algo_table,
        'active': 'charts',
    }
    return render(request, 'admin_panel/charts.html', context)


def chart_data_api(request):
    """JSON API for AJAX chart updates"""
    if not _admin_required(request):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    return JsonResponse({
        'algo': _get_algo_chart_data(),
        'distribution': _get_prediction_dist(),
    })


def detection_ratio_view(request):
    if not _admin_required(request):
        return redirect('admin_login')

    DetectionRatio.objects.all().delete()
    total = StudentPrediction.objects.count()
    ratios = []
    if total > 0:
        for label in ['Excellent', 'Good', 'Average', 'Poor']:
            cnt = StudentPrediction.objects.filter(prediction=label).count()
            if cnt > 0:
                r = DetectionRatio.objects.create(
                    label=label, count=cnt,
                    ratio=round((cnt / total) * 100, 2)
                )
                ratios.append(r)

    return render(request, 'admin_panel/detection_ratio.html',
                  {'ratios': ratios, 'active': 'charts'})
