
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from django.http import HttpResponse
import csv
from datetime import date
from .models import Exercise, DayPlan, SetEntry, Workout, WeeklySummary

def suggested_next(weight, reps, ex):
    if ex.ex_type=='cardio':
        return (None, (reps or 0)+2 if reps else None)
    if weight is not None:
        inc = 5 if ex.ex_type=='compound' else 2.5
        return (weight+inc, reps)
    if reps is not None and ex.reps_max:
        if reps < ex.reps_max:
            return (weight, reps+1)
    return (weight, reps)

from .forms import DaySelectForm

@login_required
def home(request):
    day_form=DaySelectForm(request.GET or None)
    selected_day= day_form.cleaned_data['day'] if day_form.is_valid() else 'Monday (Push)'
    plan=DayPlan.objects.get(day=selected_day)
    items = plan.items.select_related("exercise").all()

    if request.method=="POST":
        w=Workout.objects.create(user=request.user, date=date.today(), day_label=selected_day, notes="")
        for it in items:
            ex=it.exercise
            wv=request.POST.get(f"w_{ex.id}") or None
            rv=request.POST.get(f"r_{ex.id}") or None
            tv=request.POST.get(f"t_{ex.id}") or None
            nv=request.POST.get(f"n_{ex.id}") or ""
            if any([wv,rv,tv]):
                SetEntry.objects.create(workout=w, exercise=ex,
                    weight_lbs=(float(wv) if wv else None),
                    reps=(int(rv) if rv else None),
                    time_min=(float(tv) if tv else None),
                    note=nv)
        return redirect("log")

    last={}
    for it in items:
        ex=it.exercise
        s=SetEntry.objects.filter(workout__user=request.user, exercise=ex).order_by("-workout__date","-id").first()
        last[ex.id]=s
    suggestions={}
    for it in items:
        ex=it.exercise; s=last.get(ex.id)
        if s: weight,reps = suggested_next(s.weight_lbs, s.reps, ex)
        else: weight,reps = (None,None)
        suggestions[ex.id]={"weight":weight,"reps":reps}

    return render(request,"tracker/home.html",{
        "day_form":day_form,"selected_day":selected_day,"items":items,
        "last":last,"suggestions":suggestions
    })

@login_required
def log_view(request):
    workouts=Workout.objects.filter(user=request.user).order_by("-date","-id")[:50]
    return render(request,"tracker/log.html",{"workouts":workouts})

@login_required
def dashboard(request):
    import collections
    def iso_week(d): return d.isocalendar().week
    keys=["Barbell Squat","Romanian Deadlift","Barbell Bench Press"]
    qs=SetEntry.objects.filter(workout__user=request.user, exercise__name__in=keys,
                               weight_lbs__isnull=False, reps__isnull=False).select_related("workout","exercise")
    weeks=collections.OrderedDict((w,{"squat":None,"rdl":None,"bench":None,"cardio":0,"volume":0}) for w in range(1,53))
    for s in qs:
        w=iso_week(s.workout.date); name=s.exercise.name
        if name=="Barbell Squat": weeks[w]["squat"]=s.weight_lbs
        if name=="Romanian Deadlift": weeks[w]["rdl"]=s.weight_lbs
        if name=="Barbell Bench Press": weeks[w]["bench"]=s.weight_lbs
        weeks[w]["volume"] += s.volume
    for s in SetEntry.objects.filter(workout__user=request.user, time_min__isnull=False):
        w=iso_week(s.workout.date); weeks[w]["cardio"] += s.time_min or 0
    labels=list(weeks.keys())
    data = {
        "labels": labels,
        "squat_series": [weeks[w]["squat"] for w in labels],
        "rdl_series": [weeks[w]["rdl"] for w in labels],
        "bench_series": [weeks[w]["bench"] for w in labels],
        "cardio_series": [weeks[w]["cardio"] for w in labels],
        "volume_series": [weeks[w]["volume"] for w in labels],
        "prs":[_recent(request.user,n) for n in keys+["Trap Bar Deadlift"]]
    }
    return render(request,"tracker/dashboard.html",data)

def _recent(user, ex_name):
    s=SetEntry.objects.filter(workout__user=user, exercise__name=ex_name, weight_lbs__isnull=False).order_by("-workout__date","-id").first()
    if not s: return {"exercise":ex_name,"weight":None,"reps":None,"when":"-"}
    return {"exercise":ex_name,"weight":s.weight_lbs,"reps":s.reps,"when":s.workout.date.isoformat()}

@login_required
def weekly_summary(request):
    if request.method=="POST":
        week_label=request.POST.get("week_label")
        ws,_=WeeklySummary.objects.get_or_create(user=request.user, week_label=week_label)
        def setf(k):
            v=request.POST.get(k,"").strip()
            if k in ["bodyweight_lbs","avg_sleep_hrs","avg_rpe","steps_k_per_day"]:
                setattr(ws, k, float(v) if v else None)
            else:
                setattr(ws, k, v)
        for k in ["bodyweight_lbs","avg_sleep_hrs","avg_rpe","steps_k_per_day","notes"]:
            setf(k)
        ws.save()
    summaries=WeeklySummary.objects.filter(user=request.user).order_by("week_label")
    week_choices=[f"Week {i}" for i in range(1,53)]
    return render(request,"tracker/weekly_summary.html",{"summaries":summaries,"week_choices":week_choices})

@login_required
def export_csv(request):
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename="workout_log.csv"'
    writer=csv.writer(response)
    writer.writerow(["date","day","exercise","weight_lbs","reps","time_min","volume","note"])
    qs=SetEntry.objects.filter(workout__user=request.user).select_related("workout","exercise").order_by("workout__date","id")
    for s in qs:
        writer.writerow([s.workout.date.isoformat(), s.workout.day_label, s.exercise.name, s.weight_lbs or "", s.reps or "", s.time_min or "", s.volume, s.note])
    return response
