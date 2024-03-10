import uuid
import random
import string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def generate_security_token():
    return uuid.uuid4().hex[:6].upper()


def generate_id():
    return uuid.uuid4()


def generate_short_url(length=10):
    from .models import Lobby

    characters = string.ascii_letters + string.digits
    short_code = "".join(random.choice(characters) for _ in range(length))

    # Check if the short code already exists
    if Lobby.objects.filter(url_code=short_code).exists():
        return generate_short_url(length=length)
    else:
        return short_code


def send_group_message(group_name, action, data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "lobby_message",
            "action": action,
            "data": data,
        },
    )
