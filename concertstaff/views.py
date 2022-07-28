from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core import exceptions
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormView

from concert.emails import generate_ticket_email, send_mail
from concert.models import Ticket, Concert
from concertstaff import forms
from concertstaff.models import Issue


class StaffMemberRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class MainView(StaffMemberRequiredMixin, View):
    template_name = 'main_staff.html'

    def get(self, request):
        concerts = Concert.objects.all()
        issues = Issue.objects.all()
        return render(request, self.template_name, {
            'user': request.user,
            'concerts': [obj for obj in concerts if obj.is_active],
            'concerts_done': [obj for obj in concerts if not obj.is_active],
            'working_issues': issues.filter(manager=request.user, is_closed=False),
            'available_issues': issues.filter(manager=None, is_closed=False),
        })


class StatView(StaffMemberRequiredMixin, View):
    def get(self, request, concert):
        get_object_or_404(Concert, id=concert)
        return render(request, "stat.html", {'concert_id': concert})


class TicketCheckView(StaffMemberRequiredMixin, View):
    def get(self, request, ticket, sha):
        ticket = get_object_or_404(
            Ticket.objects.select_related('transaction', 'transaction__user', 'transaction__concert'), number=ticket)

        if sha != ticket.get_hash():
            return HttpResponseBadRequest('Invalid sha hash')

        return render(request, 'submit_ticket.html', {
            'ticket': ticket,
            'show_use_button': timezone.now().date() == ticket.transaction.concert.start_date_time.date()
        })

    def post(self, request, ticket, sha):
        ticket = get_object_or_404(
            Ticket.objects.select_related('transaction', 'transaction__user', 'transaction__concert'), number=ticket)

        if sha != ticket.get_hash():
            return HttpResponseBadRequest('Invalid sha hash')

        action = request.POST.get('action')
        if action == 'use':
            ticket.is_active = False
            ticket.save()
        elif action == 'change_email':
            email = request.POST.get('email')
            send_email = request.POST.get('send_email')

            user = ticket.transaction.user
            user.email = email
            user.save()

            if send_email == 'on':
                send_mail(**generate_ticket_email(ticket.transaction, headers=True))

        return render(request, 'submit_ticket.html', {
            'ticket': ticket,
            'show_use_button': timezone.now().date() == ticket.transaction.concert.start_date_time.date()
        })


class AddTicketFormView(StaffMemberRequiredMixin, FormView):
    template_name = 'free_ticket.html'
    form_class = forms.AddTicketForm
    created = False

    def get_context_data(self, **kwargs):
        kwargs['created'] = self.created
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        if form.send_email(self.request):
            self.created = True
            return self.render_to_response(self.get_context_data())
        else:
            return HttpResponse("Необходимо создать Price с нулевой ценой, обратитесь к администратору.")


class SubmitNumberView(StaffMemberRequiredMixin, TemplateResponseMixin, View):
    template_name = 'submit_ticket_number.html'

    def get(self, request):
        return self.render_to_response({})

    def post(self, request):
        number = request.POST.get('ticket', '')
        try:
            ticket = Ticket.objects.get(number=number)
        except exceptions.ObjectDoesNotExist:
            return self.render_to_response({'number': number})

        return redirect('staff-ticket-check', ticket=number, sha=ticket.get_hash())


class IssuePageView(StaffMemberRequiredMixin, TemplateView):
    template_name = 'issue.html'
    issue = None

    def get_context_data(self, **kwargs):
        is_manager = self.request.user == self.issue.manager
        kwargs.update({
            'issue': self.issue,
            'manager': 'вы' if is_manager else self.issue.manager,
            'is_manager': is_manager,
        })
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.issue = get_object_or_404(Issue, id=kwargs['issue'])
        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        self.issue = get_object_or_404(Issue, id=kwargs['issue'])
        action = request.POST.get('action')
        if action == 'get_task':
            if self.issue.manager is None:
                self.issue.manager = request.user
                self.issue.save()
            else:
                return  # raise exception
        if action == 'done_task':
            if self.issue.manager == request.user:
                self.issue.is_closed = True
                self.issue.save()
            else:
                return
        return self.render_to_response(self.get_context_data(**kwargs))


class QRCodeView(StaffMemberRequiredMixin, TemplateView):
    template_name = 'qrcode.html'
