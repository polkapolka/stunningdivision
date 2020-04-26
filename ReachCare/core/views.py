from django.shortcuts import render
from django.contrib.auth import views as auth_views

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from twilio.twiml.messaging_response import MessagingResponse

from core.models import UserQuestionnaire


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
    user_questionnaire.save()

    # Start our TwiML response
    resp = MessagingResponse()

    # Add a text message
    msg = resp.message(get_response(user_questionnaire))

    return HttpResponse(str(resp))


def get_response(user_questionnaire):
    if (
            user_questionnaire.wants_questionnaire is False or
            user_questionnaire.is_experiencing_symptoms is False or
            user_questionnaire.is_high_risk is False
    ):
        return "Questionnaire has ended."

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


