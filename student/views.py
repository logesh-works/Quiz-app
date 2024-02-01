from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta,datetime
from django.utils import timezone
from quiz import models as QMODEL
from teacher import models as TMODEL
from django.contrib import messages



#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/studentsignup.html',context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    student = models.Student.objects.get(user=request.user)
    attempted_exams = QMODEL.Result.objects.filter(student=student).values_list('exam__id', flat=True)
    
    # Exclude the exams already attempted by the student
    courses = QMODEL.Course.objects.exclude(id__in=attempted_exams)
    
    return render(request, 'student/student_exam.html', {'courses': courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    questions = QMODEL.Question.objects.all().filter(course=course)

    # Check if the student has already attempted the quiz
    if QMODEL.Result.objects.filter(exam=course, student__user=request.user).exists():
        messages.error(request, 'You have already attempted this quiz.')
        return redirect('student-dashboard')  # Redirect to the student dashboard or another appropriate page

    if request.method == 'POST':
        # Process the form data if needed
        pass
    quiz_start_time_str = timezone.now().isoformat()  # Convert datetime to string
    request.session['quiz_start_time'] = quiz_start_time_str
    request.session['total_time'] = course.total_time
    response = render(request, 'student/start_exam.html', {'course': course, 'questions': questions})
    response.set_cookie('course_id', course.id)
    return response


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course=QMODEL.Course.objects.get(id=course_id)
        
        total_marks=0
        questions=QMODEL.Question.objects.all().filter(course=course)
        for i in range(len(questions)):
            
            selected_ans = request.COOKIES.get(str(i+1))
            actual_answer = questions[i].answer
            if selected_ans == actual_answer:
                total_marks = total_marks + questions[i].marks
        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.marks=total_marks
        result.exam=course
        result.student=student
        result.save()

        return HttpResponseRedirect('view-result')
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_exam(request,pk):
    if pk is not None:
        course_id = pk
        course = QMODEL.Course.objects.get(id=course_id)
        
        total_marks = 0
        questions = QMODEL.Question.objects.all().filter(course=course)
        results = []

        for i in range(len(questions)):
            selected_ans = request.COOKIES.get(str(i + 1)).lower()
            actual_answer = questions[i].answer.lower()
            awarded_marks = questions[i].marks if selected_ans == actual_answer else 0
            is_correct = "Correct Answer" if selected_ans == actual_answer else "Wrong Answer"
            if(actual_answer == 'option1'):
                correct_answer_text = questions[i].option1
            elif(actual_answer == 'option2'):
                correct_answer_text = questions[i].option2
            elif(actual_answer == 'option3'):
                correct_answer_text = questions[i].option3
            elif(actual_answer == 'option4'):
                correct_answer_text = questions[i].option4
            if(selected_ans == 'option1'):
                select_answer_text = questions[i].option1
            elif(selected_ans == 'option2'):
                select_answer_text = questions[i].option2
            elif(selected_ans == 'option3'):
                select_answer_text = questions[i].option3
            elif(selected_ans == 'option4'):
                select_answer_text = questions[i].option4
            else:
                select_answer_text ="Skiped Question"

            result_info = {
                'question': questions[i].question,
                'correct_answer': correct_answer_text,
                'your_answer': select_answer_text,
                'awarded_marks': awarded_marks,
                'is_correct': is_correct,
            }
            
            results.append(result_info)

            if is_correct:
                total_marks += awarded_marks

        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.marks = total_marks
        result.exam = course
        result.student = student
        result.save()

        return render(request, 'student/check_exam.html', {'results': results, 'total_marks': total_marks, 'course': course})

    return HttpResponseRedirect('view-result')   



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/view_result.html',{'courses':courses})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.filter(exam=course, student=student).order_by('-id').first()
    return render(request,'student/check_marks.html',{'results':results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_marks.html',{'courses':courses})
  