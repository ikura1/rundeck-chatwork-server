import os
import requests
import emoji
import xmltodict
import json

CHAT_API_TOKEN = os.getenv("CHATWORKTOKEN", "localhost")
CHAT_ROOM_ID = os.getenv("ROOM_ID", "4649")
CHAT_BASE_URL = "https://api.chatwork.com/v2"
USERS = json.loads(os.getenv("USERS", "{}"))


def rundeck(request):
    content_dict = xmltodict.parse(request.data)["notification"]
    mentions, message = create_message(content_dict)
    return str(send_message(mentions, message))


def create_message(content_dict):
    execution_id = content_dict["@executionId"]
    status = content_dict["@status"]
    execution = content_dict["executions"]["execution"]
    project = execution["@project"]
    job_name = execution["job"]["name"]
    url = execution["@href"]
    mentions = []
    if status == "failed":
        mentions = [f"{{{user}}}" for user in USERS.keys()]
    state_emoji = {
        "running": ":arrows_counterclockwise:",
        "succeeded": ":white_check_mark:",
        "failed": ":x:",
    }
    # FIXME: emojiが出ない
    info_list = [f"url: {url}"]
    info_message = "\n".join(info_list)
    title = f"[{state_emoji[status]}:{status}] {project} / {job_name} {execution_id}"
    message = f"[info][title]{title}[/title]{info_message}[/info]"
    return mentions, emoji.emojize(message, use_aliases=True)


def send_message(mentions, message, room_id=None):
    if room_id is None:
        room_id = CHAT_ROOM_ID
    base_url = CHAT_BASE_URL
    token = CHAT_API_TOKEN
    user_dict = USERS
    mention_template = "[To:{id}] {name}さん\n"
    mention_templates = {
        k: mention_template.format_map(v) for k, v in user_dict.items()
    }

    mention_text = "".join(
        [mention.format_map(mention_templates) for mention in mentions]
    )
    message = message.format_map({k: v["name"] for k, v in user_dict.items()})
    message = mention_text + message
    post_message_url = "{0}/rooms/{1}/messages".format(base_url, room_id)

    headers = {"X-ChatWorkToken": token}
    params = {"body": message}
    r = requests.post(post_message_url, headers=headers, params=params)
    return r

