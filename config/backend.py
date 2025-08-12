import jwt
import json
import logging
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

# Configure logging
logger = logging.getLogger(__name__)

class MyOIDCAB(OIDCAuthenticationBackend):

    def filter_users_by_claims(self, claims):
        email = claims.get("email")
        if not email:
            return self.UserModel.objects.none()
        if email:
            return self.UserModel.objects.filter(email=email)
        sub = claims.get("sub")
        if sub:
            users = self.UserModel.objects.filter(sub=sub)
            if users.exists():
                return users

        return self.UserModel.objects.filter(email=email)

    def get_userinfo(self, access_token, id_token, payload):
        # IDトークンを署名検証せずにデコード（デバッグ用）
        try:
            decoded = jwt.decode(id_token, options={"verify_signature": False})
            pretty_claims = json.dumps(decoded, indent=2, ensure_ascii=False)
            logger.debug("Decoded ID Token claims:\n%s", pretty_claims)
        except Exception as e:
            logger.error("Failed to decode ID Token: %s", e)

        return super().get_userinfo(access_token, id_token, payload)

    def get_user_details(self, claims):
        """
        Override this method to customize how user details are extracted from claims.
        This is called when a user logs in via OIDC.
        """
        user_details = super(MyOIDCAB, self).get_user_details(claims)
        
        # Extract email and other details from claims
        user_details['email'] = self._get_email_from_claims(claims)
        user_details['sub'] = claims.get('sub', '')
        user_details['first_name'] = claims.get('given_name', '')
        user_details['last_name'] = claims.get('family_name', '')

        return user_details

    def _get_email_from_claims(self, claims):
        # claims に emails でしか返ってこない場合はここをカスタムする
        email = claims.get('email', '')

        return email

    def create_user(self, claims):
        """
        CustomUserManager.create_user() の email 引数重複回避。
        claims から email を抜き出して、キーワード引数に重複しないようにする。
        """
        # 既存ユーザーがいれば返す
        users = self.filter_users_by_claims(claims)
        if users.exists():
            return users.first()

        # 新規ユーザー作成
        email = self._get_email_from_claims(claims)
        sub = claims.get('sub', '')
        first_name = claims.get('given_name', 'first_name')
        last_name = claims.get('family_name', 'last_name')

        return self.UserModel.objects.create_user(
            email=email,
            sub=sub,
            password=None,
            first_name=first_name,
            last_name=last_name,
        )

    def update_user(self, user, claims):
        user.email = self._get_email_from_claims(claims)
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.sub = claims.get('sub', '')
        user.save()

        return user