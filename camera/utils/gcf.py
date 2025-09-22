import os
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def invoke_take_picture_function(user, group_id='group_id'):
    """
    撮影リクエストを Cloud Function に送り、
    Cloud Function が保存した gcs_id を取得する
    """
    url = os.environ["TAKE_PICTURE_FUNCTION_URL"]

    payload = {
        "command": "take-a-picture",
        "owner_id": user.id,
        "group_id": group_id
    }

    # サービスアカウントで ID トークンを生成
    sa_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    credentials = service_account.IDTokenCredentials.from_service_account_info(
        sa_info, target_audience=url
    )
    credentials.refresh(Request())

    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()
    except Exception as e:
        return {"status": "error", "message": f"Cloud Function request failed: {e}"}

    try:
        data = resp.json()
    except Exception:
        data = {"status": "error", "message": f"Invalid JSON response: {resp.text}"}

    # Cloud Function から gcs_id が返ってくる想定
    if data.get("status") != "success" or "gcs_id" not in data:
        return {"status": "error", "message": data.get("message", "gcs_id not returned")}

    return {
        "status": "success",
        "gcs_id": data["gcs_id"],
        "message": data.get("message", "Photo saved successfully")
    }
