import msal
import httpx
from openai import AzureOpenAI
from app.config import settings


AUTHORITY = f"https://login.microsoftonline.com/{settings.TENANT_ID}"
SCOPES = [f"{settings.OPENAI_APP_API_ID}/.default"]


def _get_msal_app() -> msal.ConfidentialClientApplication:
    return msal.ConfidentialClientApplication(
        settings.CLIENT_ID,
        authority=AUTHORITY,
        client_credential=settings.CLIENT_SECRET,
    )


def get_openai_client() -> AzureOpenAI:
    msal_app = _get_msal_app()
    token_result = msal_app.acquire_token_for_client(scopes=SCOPES)

    if "access_token" not in token_result:
        raise RuntimeError(f"Failed to get access token: {token_result.get('error_description')}")

    return AzureOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_VERSION,
        azure_ad_token=token_result["access_token"],
        http_client=httpx.Client(verify=False),
    )
