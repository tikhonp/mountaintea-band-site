from django.shortcuts import render
from concert.models import Concert, Price, Transaction
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_http_methods
from concert import forms
from django.contrib.auth.models import User
from django.core import exceptions
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail

with open("debug", "r") as f:
    debug = f.read()


@require_http_methods(["GET"])
def main(request):
    return HttpResponse(str(debug))

@require_http_methods(["GET"])
def main_page(request):
    return render(request, 'main.html', {
        'concert_id': Concert.objects.all().first()
    })


@require_http_methods(["GET", "POST"])
def buy_ticket(request, concert_id):
    if concert_id is None:
        return Http404('Please provide concert id')

    concert = Concert.objects.get(id=concert_id)
    prices = Price.objects.filter(concert=concert)

    paying = False
    transaction = None

    if request.method == 'GET':
        form = forms.BuyTicketForm()

        u = request.session.get('user', False)
        if u:
            try:
                u = User.objects.get(id=u)
                p = u.profile
                print(p, p.phone)
                form = forms.BuyTicketForm({
                    'name': u.first_name,
                    'email': u.email,
                    'phone_number': p.phone,
                })
            except exceptions.ObjectDoesNotExist:
                request.session.pop('user', None)

    else:
        form = forms.BuyTicketForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.filter(
                email=cd['email'], first_name=cd['name'])
            if len(user) == 0:
                user = User.objects.create(
                    username=cd['name'].replace(" ", ""),
                    first_name=cd['name'],
                    email=cd['email']
                )
                p = user.profile
                p.phone = cd['phone_number']

                user.save()
                p.save()
            else:
                user = user.first()

            request.session['user'] = user.id
            request.session['price'] = prices.first().id

            transaction = Transaction.objects.create(
                user=user,
                price=prices.first(),
                concert=concert
            )
            transaction.save()
            paying = True

    params = {
        'concert': concert,
        'price': prices.first(),
        'form': form,
        'paying': paying,
        'transaction': transaction,
    }
    return render(request, 'buy_ticket.html', params)


@csrf_exempt
@require_http_methods(["POST"])
def incoming_payment(request):
    global  debug
    label = request.POST.get('label', '')
    try:
        transaction = Transaction.objects.get(id=int(label))
    except exceptions.ObjectDoesNotExist:
        return HttpResponse("Aborted object doesnt exist")

    p = transaction.price
    if p.price != float(request.POST['withdraw_amount']):
        return HttpResponse("Aborted price didnt match")

    transaction.is_done = True
    transaction.save()

    u = transaction.user
    send_mail(
        'Ваш билет!',
        'Поздравляю',
        'noreply@mountainteaband.ru',
        [u.email],
        fail_silently=False
    )
    with open("debug", "w") as f:
        debug = f.write(str(request.POST))
    return HttpResponse("ok")
