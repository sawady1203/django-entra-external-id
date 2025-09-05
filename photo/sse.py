import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

def notify_photo_created(photo):
    """
    最新の写真を購読中のブラウザに通知
    """
    async_to_sync(channel_layer.group_send)(
        f"user_{photo.owner.id}",  # ユーザー単位で通知
        {
            "type": "photo.created",
            "photo_id": photo.id,
            "bucket": photo.bucket,
            "name": photo.name,
            "content_type": photo.content_type,
            "size": photo.size,
        }
    )
