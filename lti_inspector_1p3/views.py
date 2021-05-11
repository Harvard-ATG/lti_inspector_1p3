from pylti1p3.tool_config import ToolConfJsonFile


def get_lti_config_path():
    return os.path.join(settings.BASE_DIR, '..', 'lti_config.json')

def get_tool_conf():
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    return tool_conf

@require_POST
def launch(request):
    tool_conf = get_tool_conf()
    launch_data_storage = get_launch_data_storage()
    message_launch = ExtendedDjangoMessageLaunch(request, tool_conf, launch_data_storage=launch_data_storage)
    message_launch_data = message_launch.get_launch_data()
    pprint.pprint(message_launch_data)

    difficulty = message_launch_data.get('https://purl.imsglobal.org/spec/lti/claim/custom', {})\
        .get('difficulty', None)
    if not difficulty:
        difficulty = request.GET.get('difficulty', 'normal')

    return render(request, 'game.html', {
        'page_title': PAGE_TITLE,
        'is_deep_link_launch': message_launch.is_deep_link_launch(),
        'launch_data': message_launch.get_launch_data(),
        'launch_id': message_launch.get_launch_id(),
        'curr_user_name': message_launch_data.get('name', ''),
        'curr_diff': difficulty
    })