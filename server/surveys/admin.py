from django.contrib import admin

from .models import Answer, Question

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline
    ]
