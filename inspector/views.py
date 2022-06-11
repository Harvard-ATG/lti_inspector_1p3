
import json
import os
from logging import getLogger
from pprint import pformat

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from pylti1p3.contrib.django import (DjangoCacheDataStorage,
                                     DjangoMessageLaunch, DjangoOIDCLogin)
from pylti1p3.tool_config import ToolConfJsonFile

logger = getLogger(__name__)


class CustomDjangoMessageLaunch(DjangoMessageLaunch):
    # Override the default validate_deployment() method from DjangoMessageLaunch since we don't want
    # to have to reconfigure the tool every time someone deploys it in a new course or sub-account.
    def validate_deployment(self):
        return self

def get_lti_config_path():
    return os.path.join(settings.BASE_DIR, 'configs', 'inspector.json')


def get_tool_conf():
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    return tool_conf


def get_launch_data_storage():
    return DjangoCacheDataStorage()


def get_launch_url(request):
    target_link_uri = request.POST.get('target_link_uri', request.GET.get('target_link_uri'))
    if not target_link_uri:
        raise Exception('Missing "target_link_uri" param')
    return target_link_uri


@csrf_exempt
def login(request):
    logger.debug('login')
    tool_conf = get_tool_conf()
    launch_data_storage = get_launch_data_storage()

    oidc_login = DjangoOIDCLogin(request, tool_conf, launch_data_storage=launch_data_storage)
    target_link_uri = get_launch_url(request)
    logger.debug(f'Target link URI: {target_link_uri}')
    return oidc_login.enable_check_cookies().redirect(target_link_uri)


@require_POST
@csrf_exempt
def launch(request):
    logger.debug('Launch request')
    tool_conf = get_tool_conf()
    launch_data_storage = get_launch_data_storage()
    message_launch = CustomDjangoMessageLaunch(request, tool_conf, launch_data_storage=launch_data_storage)
    message_launch_data = message_launch.get_launch_data()

    # use the Names and Roles Provisioning Service to get the course roster
    members = []
    if message_launch.has_nrps():
        logger.debug('Has NRPS')
        members = message_launch.get_nrps().get_members()

    # use the Assignment and Grade Service
    line_items = []
    if message_launch.has_ags():
        ags = message_launch.get_ags()
        logger.debug('Has AGS')
        line_items = ags.get_lineitems()
        x = ags.get_lineitems_page()
        logger.debug(f'AGS line items: {pformat(x)}')


    template_context = {
        'launch_params': message_launch_data,
        'launch_params_pp': json.dumps(message_launch_data, indent=4),
        'members': members,
        'line_items': line_items,
    }
    return render(request, 'inspector/index.html', template_context)


def get_jwks(request):
    tool_conf = get_tool_conf()
    return JsonResponse(tool_conf.get_jwks(), safe=False)


LTI_AGS_LINE_ITEM_SCOPE = "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem"
LTI_AGS_LINE_ITEM_READ_ONLY_SCOPE = "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly"
LTI_AGS_RESULT_READ_ONLY_SCOPE = "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly"
LTI_AGS_SCORE_SCOPE = "https://purl.imsglobal.org/spec/lti-ags/scope/score"
LTI_AGS_SHOW_PROGRESS_SCOPE = "https://canvas.instructure.com/lti-ags/progress/scope/show"
LTI_NRPS_V2_SCOPE = "https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly"
LTI_UPDATE_PUBLIC_JWK_SCOPE = "https://canvas.instructure.com/lti/public_jwk/scope/update"
LTI_ACCOUNT_LOOKUP_SCOPE = "https://canvas.instructure.com/lti/account_lookup/scope/show"
def config(request):
    oidc_initiation_url = request.build_absolute_uri(reverse('inspector-login'))
    target_link_uri = request.build_absolute_uri(reverse('inspector-launch'))
    lms_config = {
        'title': 'LTI 1.3 Inspector',
        'description': 'A tool for inspecting LTI 1.3 launch data and demonstrating LTI Advantage services',
        'oidc_initiation_url': oidc_initiation_url,
        'target_link_uri': target_link_uri,
        'scopes': [
            LTI_AGS_LINE_ITEM_SCOPE,
            LTI_AGS_LINE_ITEM_READ_ONLY_SCOPE,
            LTI_AGS_RESULT_READ_ONLY_SCOPE,
            LTI_AGS_SCORE_SCOPE,
            LTI_AGS_SHOW_PROGRESS_SCOPE,
            LTI_NRPS_V2_SCOPE,
            LTI_UPDATE_PUBLIC_JWK_SCOPE,
            LTI_ACCOUNT_LOOKUP_SCOPE,
        ],
        'extensions': [
            {
                'platform': 'canvas.instructure.com',
                'privacy_level': 'public',
                'settings': {
                    'text': 'LTI 1.3 Inspector',
                    'icon_url': 'https://www.ltiadvantage.com/wp-content/uploads/2019/01/lti-advantage-logo-white.png',
                    'placements': [
                        {
                            'placement': 'course_navigation',
                        },
                        {
                            'placement': 'account_navigation',
                        },
                    ],
                },
            }
        ],
        'public_jwk': get_tool_conf().get_jwks()['keys'][0],
        'custom_fields': {
            'custom_field_1': '$Canvas.user.integration_id',
        },
    }
    return JsonResponse(lms_config, safe=False)
