from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Goal, Note, Deadline
from .forms import GoalForm, NoteForm, DeadlineForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from .telegram_bot import run_telegram_bot


# Цели Юля
@login_required
def goal_list(request):
    query = request.GET.get('q')
    if query:
        goals = Goal.objects.filter(title__icontains=query, user=request.user)
    else:
        goals = Goal.objects.filter(user=request.user)
    goals = goals.order_by('-created_at')

    paginator = Paginator(goals, 5)  # 5 целей на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/goal_list.html', {'page_obj': page_obj, 'query': query})


@login_required
def goal_create(request):
    if request.method == 'POST':
        print("POST data:", request.POST)
        form = GoalForm(request.POST)
        if form.is_valid():
            print("Form is valid!")
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('dashboard:goal_list')
        else:
            print("Form errors:", form.errors)
    else:
        form = GoalForm()
    return render(request, 'dashboard/goal_form.html', {'form': form})


@login_required
def goal_update(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('dashboard:goal_list')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'dashboard/goal_form.html', {'form': form, 'title': 'Редактировать цель'})


@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        return redirect('dashboard:goal_list')
    return render(request, 'dashboard/goal_confirm_delete.html', {'goal': goal})


# Заметки Даша
class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'dashboard/note_list.html'
    context_object_name = 'notes'
    paginate_by = 10

    def get_queryset(self):
        qs = Note.objects.filter(user=self.request.user)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))
        return qs.order_by('-created_at')


class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'dashboard/note_form.html'
    success_url = reverse_lazy('dashboard:note_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'dashboard/note_form.html'
    success_url = reverse_lazy('dashboard:note_list')


class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    template_name = 'dashboard/note_confirm_delete.html'
    success_url = reverse_lazy('dashboard:note_list')


# Дедлайны Даша
class DeadlineListView(LoginRequiredMixin, ListView):
    model = Deadline
    template_name = 'dashboard/deadline_list.html'
    context_object_name = 'deadlines'
    paginate_by = 10

    def get_queryset(self):
        qs = Deadline.objects.filter(user=self.request.user)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(title__icontains=q)
        return qs.order_by('due_date')


class DeadlineCreateView(LoginRequiredMixin, CreateView):
    model = Deadline
    form_class = DeadlineForm
    template_name = 'dashboard/deadline_form.html'
    success_url = reverse_lazy('dashboard:deadline_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class DeadlineUpdateView(LoginRequiredMixin, UpdateView):
    model = Deadline
    form_class = DeadlineForm
    template_name = 'dashboard/deadline_form.html'
    success_url = reverse_lazy('dashboard:deadline_list')


class DeadlineDeleteView(LoginRequiredMixin, DeleteView):
    model = Deadline
    template_name = 'dashboard/deadline_confirm_delete.html'
    success_url = reverse_lazy('dashboard:deadline_list')



def start_telegram_bot(request):
    app = run_telegram_bot()
    app.run_polling(drop_pending_updates=True)
    return JsonResponse({"status": "bot started"})