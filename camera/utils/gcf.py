import os
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def invoke_take_picture_function(user, group_id='group_id'):
    url = os.environ["TAKE_PICTURE_FUNCTION_URL"]

    payload = {
        "command": "take-a-picture",
        "owner_id": user.id,
        "group_id": 'group_id'
    }

    # サービスアカウントを使ってIDトークンを生成
    sa_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    credentials = service_account.IDTokenCredentials.from_service_account_info(
        sa_info, target_audience=url
    )
    credentials.refresh(Request())

    headers = {"Authorization": f"Bearer {credentials.token}"}
    response = requests.post(url, headers=headers, json=payload)

    return response.text, response.status_code
