
from django.db import models
from django.contrib.auth.models import User

class Exercise(models.Model):
    TYPE_CHOICES=[('compound','Compound'),('isolation','Isolation'),('cardio','Cardio')]
    name=models.CharField(max_length=100, unique=True)
    ex_type=models.CharField(max_length=20, choices=TYPE_CHOICES)
    default_sets=models.IntegerField(null=True, blank=True)
    reps_min=models.IntegerField(null=True, blank=True)
    reps_max=models.IntegerField(null=True, blank=True)
    def __str__(self): return self.name

class DayPlan(models.Model):
    DAY_CHOICES=[('Monday (Push)','Monday (Push)'),('Tuesday (Legs)','Tuesday (Legs)'),
                 ('Wednesday (Pull)','Wednesday (Pull)'),('Thursday (Cardio)','Thursday (Cardio)'),
                 ('Friday (Legs 2)','Friday (Legs 2)'),('Saturday (Upper)','Saturday (Upper)')]
    day=models.CharField(max_length=30, choices=DAY_CHOICES, unique=True)
    def __str__(self): return self.day

class DayPlanExercise(models.Model):
    plan=models.ForeignKey(DayPlan, on_delete=models.CASCADE, related_name="items")
    exercise=models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order=models.IntegerField(default=1)
    note=models.CharField(max_length=200, blank=True, default="")
    class Meta:
        unique_together=("plan","exercise")
        ordering=["order"]

class Workout(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    date=models.DateField()
    day_label=models.CharField(max_length=30)
    notes=models.CharField(max_length=255, blank=True, default="")
    created_at=models.DateTimeField(auto_now_add=True)

class SetEntry(models.Model):
    workout=models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="sets")
    exercise=models.ForeignKey(Exercise, on_delete=models.CASCADE)
    weight_lbs=models.FloatField(null=True, blank=True)
    reps=models.IntegerField(null=True, blank=True)
    time_min=models.FloatField(null=True, blank=True)
    note=models.CharField(max_length=200, blank=True, default="")
    @property
    def volume(self):
        if self.weight_lbs and self.reps: return self.weight_lbs*self.reps
        return 0

class WeeklySummary(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    week_label=models.CharField(max_length=20)
    bodyweight_lbs=models.FloatField(null=True, blank=True)
    avg_sleep_hrs=models.FloatField(null=True, blank=True)
    avg_rpe=models.FloatField(null=True, blank=True)
    steps_k_per_day=models.FloatField(null=True, blank=True)
    notes=models.CharField(max_length=255, blank=True, default="")

class PersonalRecord(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    exercise=models.ForeignKey(Exercise, on_delete=models.CASCADE)
    date=models.DateField()
    weight_lbs=models.FloatField()
    reps=models.IntegerField()
    class Meta: unique_together=("user","exercise","date","weight_lbs","reps")
