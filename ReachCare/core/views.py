from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse

from core.models import UserQuestionnaire

INVALID_RESPONSE_MESSAGE = "Sorry, I didn't understand that. " \
                           "Please reply with one of the given options."

YES_NO_TEXT = "Reply 1 for Yes, 2 for No"

GET_HELP_MESSAGE = "Please call 911 or go to the nearest hospital."

WELCOME_TEXT = "Welcome to ReachCare. " \
               "If you’re having a medical emergency or severe symptoms of fever, cough, " \
               f"and shortness of breath: {GET_HELP_MESSAGE} " \
               "If you’d like to find a COVID-19 testing center near you, " \
               "please answer the following questions. " \
               "Would you like to proceed?"

INSURANCE_QUESTION = "Are you able to get tested through your insurance?"

HAS_INSURANCE_RESPONSE = "Please call your insurance for more info."

SYMPTOM_QUESTION = "Are you experiencing fever, cough, or shortness of breath?"

SYMPTOM_SEVERITY_QUESTION = "How are your symptoms?"
SYMPTOM_SEVERITY_OPTIONS = "Press 1 for Mild or Moderate, 2 for Severe or Worsening."

ZIP_CODE_QUESTION = "What is your zip code?"
NO_TESTINGS_SITE_FOUND = "Unable to find a testing site."

TESTING_UNNECESSARY_TEXT = "You don’t need to get tested for Covid 19 at this time. "

THANK_YOU_TEXT = "Thanks for using ReachCare! Respond with RESTART to start over."


def should_restart(current_text):
    clean_text = current_text.lower().strip()
    if clean_text == "restart":
        return True
    return False


@csrf_exempt
def sms_response(request):
    user_id = request.POST.get('From', None)
    current_text = request.POST.get('Body', "")
    if user_id is None:
        return HttpResponseBadRequest("No user id found in post 'From' field")

    if should_restart(current_text):
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
        resp.message(INVALID_RESPONSE_MESSAGE)
    resp.message(response_message)

    return HttpResponse(str(resp))


def get_response_message(user_questionnaire):
    if user_questionnaire.wants_questionnaire is False:
        return THANK_YOU_TEXT

    if user_questionnaire.can_get_provider_test is True:
        return f"{HAS_INSURANCE_RESPONSE}\n{THANK_YOU_TEXT}"

    if user_questionnaire.is_experiencing_symptoms is False:
        return f"{TESTING_UNNECESSARY_TEXT}\n{THANK_YOU_TEXT}"

    if user_questionnaire.has_severe_worsening_symptoms:
        return f"{GET_HELP_MESSAGE}\n{THANK_YOU_TEXT}"

    if user_questionnaire.wants_questionnaire is None:
        return f"{WELCOME_TEXT}\n{YES_NO_TEXT}"

    if user_questionnaire.can_get_provider_test is None:
        return f"{INSURANCE_QUESTION}\n{YES_NO_TEXT}"

    if user_questionnaire.is_experiencing_symptoms is None:
        return f"{SYMPTOM_QUESTION}\n{YES_NO_TEXT}"

    if user_questionnaire.has_severe_worsening_symptoms is None:
        return f"{SYMPTOM_SEVERITY_QUESTION}\n{SYMPTOM_SEVERITY_OPTIONS}"

    if user_questionnaire.zip_code is None:
        return ZIP_CODE_QUESTION

    if user_questionnaire.zip_code is not None:
        closest_testing_site = user_questionnaire.get_closest_testing_site()
        if closest_testing_site is None:
            return NO_TESTINGS_SITE_FOUND
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
