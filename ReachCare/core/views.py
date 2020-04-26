from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse

from core.models import UserQuestionnaire

INVALID_RESPONSE_MESSAGE = "Sorry, I didn't understand that. " \
                           "Please reply with one of the given options."

YES_NO_TEXT = "Reply 1 for Yes, 2 for No"

WELCOME_TEXT = "Welcome to ReachCare. Would you like to proceed with the questionnaire?"

INSURANCE_QUESTION = "Are you able to get tested through insurance or a medical provider?"

HAS_INSURANCE_RESPONSE = "Please contact your insurance provider."

SYMPTOM_QUESTION = "Are you experiencing fever, cough, or shortness of breath?"

SYMPTOM_SEVERITY_QUESTION = "How are your symptoms?"
SYMPTOM_SEVERITY_OPTIONS = "Press 1 for Mild, 2 for Severe or Worsening."

ZIP_CODE_QUESTION = "What is your zip code?"

TESTING_UNNECESSARY_TEXT = "You don’t need to get tested for Covid 19 at this time."

THANK_YOU_TEXT = "Thanks for using ReachCare! Respond with RESTART to start over."


def should_restart(current_text):
    clean_text = current_text.lower().strip()
    if clean_text == "restart":
        return True
    return False


@csrf_exempt
def sms_response(request):
    user_id = request.POST.get('From', None)
    current_text = request.POST.get('Body', None)

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

    if (
            user_questionnaire.has_severe_worsening_symptoms is False or
            user_questionnaire.is_experiencing_symptoms is False
    ):
        return f"{TESTING_UNNECESSARY_TEXT}\n{THANK_YOU_TEXT}"

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
