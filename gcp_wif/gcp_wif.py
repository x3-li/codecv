# pip install google-auth google-auth-httplib2 requests google-cloud-aiplatform

import google.auth.transport.requests
from google.auth import identity_pool
from google.auth.external_account import SupplierContext
from google.cloud import aiplatform


class KeycloakSubjectTokenSupplier(identity_pool.SubjectTokenSupplier):
    """
    从你自己的应用上下文中返回当前用户的 Keycloak OIDC ID Token。
    注意：这里应返回 OIDC ID Token，而不是随便一个 access token。
    """

    def __init__(self, get_token_func):
        self._get_token_func = get_token_func

    def get_subject_token(
        self,
        context: SupplierContext,
        request: google.auth.transport.requests.Request,
    ) -> str:
        token = self._get_token_func()

        if not token:
            raise ValueError("Keycloak subject token is empty.")

        # 这里建议你自己加上缓存、过期判断、日志等
        return token


def get_current_keycloak_id_token() -> str:
    """
    这里替换成你自己的取 token 逻辑。
    例如：
    - 从当前 session 里取
    - 从后端安全存储里取
    - 从前端 Bearer token 透传后校验并提取
    """
    # 示例：假设你已经拿到了当前用户的 Keycloak ID token
    return "<KEYCLOAK_ID_TOKEN>"


def build_google_credentials():
    supplier = KeycloakSubjectTokenSupplier(get_current_keycloak_id_token)

    credentials = identity_pool.Credentials(
        audience="//iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID",
        subject_token_type="urn:ietf:params:oauth:token-type:id_token",
        token_url="https://sts.googleapis.com/v1/token",
        service_account_impersonation_url=(
            "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/"
            "SERVICE_ACCOUNT_EMAIL:generateAccessToken"
        ),
        credential_source=None,
        subject_token_supplier=supplier,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return credentials


def main():
    credentials = build_google_credentials()

    # 触发 token exchange
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)

    print("Google access token acquired.")
    print("Token prefix:", credentials.token[:20])

    # 下面示例是给 Vertex AI 用
    aiplatform.init(
        project="YOUR_PROJECT_ID",
        location="asia-northeast1",
        credentials=credentials,
    )

    # 这里只是演示能初始化 client
    print("Vertex AI client initialized.")


if __name__ == "__main__":
    main()