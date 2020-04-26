from django.shortcuts import render
from django.contrib.auth import views as auth_views

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from twilio.twiml.messaging_response import MessagingResponse

from core.models import UserQuestionnaire
from core.forms import LoginForm


@csrf_exempt
def sms_response(request):
    user_id = request.POST.get('From', None)
    current_text = request.POST.get('Body', None)

    if current_text == "RESTART":
        try:
            uq = UserQuestionnaire.objects.get(user_id=user_id)
            uq.delete()
        except UserQuestionnaire.DoesNotExist:
            pass

    user_questionnaire, created = UserQuestionnaire.objects.get_or_create(user_id=user_id)
    if not created:
        user_questionnaire.process_response(current_text)

    response_message = get_response_message(user_questionnaire)

    original_message = user_questionnaire.last_message_sent
    user_questionnaire.last_message_sent = response_message
    user_questionnaire.save()

    # Start our TwiML response
    resp = MessagingResponse()

    # If we send the same message twice, that means the user's text wasn't understandable
    if original_message is not None and original_message == response_message:
        resp.message("Sorry, I didn't understand that. Please reply with one of the given options.")
    resp.message(response_message)

    return HttpResponse(str(resp))


def get_response_message(user_questionnaire):
    if (
            user_questionnaire.wants_questionnaire is False or
            user_questionnaire.is_experiencing_symptoms is False or
            user_questionnaire.is_high_risk is False
    ):
        return "Questionnaire has ended. Respond with RESTART to start over."

    if user_questionnaire.wants_questionnaire is None:
        return "Welcome to the questionnaire. Would you like to proceed? (Y/N)"

    if user_questionnaire.is_experiencing_symptoms is None:
        return "Are you experiencing symptoms? (Y/N)"

    if user_questionnaire.is_high_risk is None:
        return "Are you high risk? (Y/N)"

    if user_questionnaire.has_severe_worsening_symptoms is None:
        return "Are your symptoms 1. Mild 2. Severe 3. Worsening?"

    if user_questionnaire.preferred_testing_site_type is None:
        return "What is you preferred testing site type? 1. Walk up 2. Drive through"

    if user_questionnaire.zip_code is None:
        return "What is your zip code?"

    if user_questionnaire.zip_code is not None:
        closest_testing_site = user_questionnaire.get_closest_testing_site()
        return closest_testing_site.as_text()


def home_view(request):
    return render(request, 'core/home.html')


def account_view(request):
    return render(request, 'core/account.html')


def login_view(request):
    # login_form = LoginForm()
    return render(request, 'core/login.html'
                  # ,{"login_form":login_form}
                  )

def logout_view(request):
    return render(request, 'core/logout.html'
                  )
