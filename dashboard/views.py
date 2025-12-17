from django.shortcuts import render

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Note, Deadline
from .forms import NoteForm, DeadlineForm


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
    success_url = reverse_lazy('note_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'dashboard/note_form.html'
    success_url = reverse_lazy('note_list')

class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    template_name = 'dashboard/note_confirm_delete.html'
    success_url = reverse_lazy('note_list')

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
    success_url = reverse_lazy('deadline_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class DeadlineUpdateView(LoginRequiredMixin, UpdateView):
    model = Deadline
    form_class = DeadlineForm
    template_name = 'dashboard/deadline_form.html'
    success_url = reverse_lazy('deadline_list')

class DeadlineDeleteView(LoginRequiredMixin, DeleteView):
    model = Deadline
    template_name = 'dashboard/deadline_confirm_delete.html'
    success_url = reverse_lazy('deadline_list')
