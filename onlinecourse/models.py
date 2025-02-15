import sys
from django.utils.timezone import now
try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

from django.conf import settings
import uuid


# Instructor model
class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username


# Learner model
class Learner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return self.user.username + "," + \
               self.occupation


# Course model
class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return "Name: " + self.name + "," + \
               "Description: " + self.description


# Lesson model
class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return "Title: {}, Order: {}, Course: {}, Content: {}".format(
            self.title,
            self.order,
            self.course.name,
            self.content
        )


# Enrollment model
# <HINT> Once a user enrolled a class, an enrollment entry should be created between the user and course
# And we could use the enrollment to track information such as exam submissions
class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)

    def __str__(self):
        return "User: {}, Course: {}, Date Enrolled: {}, Mode: {}, Rating: {}".format(
            self.user.name,
            self.course.name,
            self.date_enrolled,
            self.mode,
            self.rating
        )


class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    question_text = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        default="Question"
    )
    grade = models.IntegerField(
        null=False,
        blank=False,
        default=1
    )

    def __str__(self):
        return "Lesson: {}, Question: {}, Grade: {}".format(
            self.lesson.pk,
            self.question_text,
            self.grade
        )

    def get_score(self, selected):
        choices = self.choice_set.all()
        selected_count = selected.filter(question__id=self.id,is_correct=True).count()
        total_items = choices.count()
        correct = 0
        if selected_count > 0:
            for choice in choices:
                if choice.is_correct == True and choice in selected:
                    correct += 1
                elif choice.is_correct == False and choice not in selected:
                    correct += 1
        percentage = correct / total_items
        points = percentage * self.grade
        print("###### Q{} {}/{} = {}, {}/{}".format(self.id, correct, total_items, percentage, points, self.grade))
        return points, self.grade

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        default="Choice *"
    )
    is_correct = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return "choice_text: {}, is_correct: {}, Question: {}".format(
            self.choice_text,
            self.is_correct,
            self.question.question_text,
        )

class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)
    def __str__(self):
        return "Enrollment: {}, Choices: {}".format(self.enrollment.mode, len(self.choices))
