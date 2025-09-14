
from django.contrib import admin
from .models import Exercise, DayPlan, DayPlanExercise, Workout, SetEntry, WeeklySummary, PersonalRecord
class DayPlanExerciseInline(admin.TabularInline):
    model=DayPlanExercise; extra=0
@admin.register(DayPlan)
class DayPlanAdmin(admin.ModelAdmin):
    inlines=[DayPlanExerciseInline]; list_display=("day",)
@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display=("name","ex_type","default_sets","reps_min","reps_max"); search_fields=("name",)
@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display=("user","date","day_label","created_at"); search_fields=("user__username","day_label")
admin.site.register(SetEntry); admin.site.register(WeeklySummary); admin.site.register(PersonalRecord)
