from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Goal
from .forms import GoalForm


# Create your views here.
#@login_required
def goal_list(request):
    if request.user.is_authenticated:
        goals = Goal.objects.filter(user=request.user).order_by('-created_at')
    else:
        goals = Goal.objects.all().order_by('-created_at')
    return render(request, 'dashboard/goal_list.html', {'goals': goals})

#@login_required
def goal_create(request):
    if not request.user.is_authenticated:
        from django.contrib.auth.models import User
        user, _ = User.objects.get_or_create(username='demo_user')
    else:
        user = request.user
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('goal_list')
    else:
        form = GoalForm()
    return render(request, 'dashboard/goal_create.html', {'form': form})