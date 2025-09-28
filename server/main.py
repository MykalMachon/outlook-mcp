from fastmcp import FastMCP
from fastmcp.server.auth.providers.azure import AzureProvider
from fastmcp.server.dependencies import get_access_token
from fastmcp.server.context import Context

from msgraph import GraphServiceClient
from msgraph.generated.users.item.messages.messages_request_builder import (
    MessagesRequestBuilder,
)
from kiota_abstractions.base_request_configuration import RequestConfiguration

from azure.core.credentials import AccessToken
from kiota_authentication_azure.azure_identity_authentication_provider import (
    AzureIdentityAuthenticationProvider,
)

from datetime import datetime
import time

from os import getenv
from dotenv import load_dotenv

load_dotenv()


# Custom credentials wrapper for existing token
class TokenCredentials:
    def __init__(self, access_token: str, expires_on: int = None):
        self.access_token = access_token
        # Set expiration to 1 hour from now if not provided
        self.expires_on = expires_on or int(time.time()) + 3600

    def get_token(self, *scopes, **kwargs):
        return AccessToken(self.access_token, self.expires_on)


# Create a wrapper class to force v2.0 behavior
class PatchedAzureProvider(AzureProvider):
    def _get_resource_url(self, mcp_path):
        return None  # Force v2.0 behavior

    def authorize(self, *args, **kwargs):
        kwargs.pop("resource", None)
        return super().authorize(*args, **kwargs)


def load_config():
    host = getenv("HOST") if getenv("HOST") else "localhost"
    port = getenv("PORT") if getenv("PORT") else "3000"

    return {
        "host": host,
        "port": port,
        "base_url": (
            getenv("BASE_URL") if getenv("BASE_URL") else f"http://{host}:{port}"
        ),
        "azure_config_url": getenv("AZURE_CONFIG_URL"),
        "azure_tenant_id": getenv("AZURE_TENANT_ID"),
        "azure_client_id": getenv("AZURE_CLIENT_ID"),
        "azure_client_secret": getenv("AZURE_CLIENT_SECRET"),
    }


def main():
    config = load_config()
    print(config)

    # initialize oidc proxy
    auth = PatchedAzureProvider(
        client_id=config.get("azure_client_id"),
        tenant_id=config.get("azure_tenant_id"),
        client_secret=config.get("azure_client_secret"),
        base_url=config.get("base_url"),
        required_scopes=[
            "User.Read",
            "email",
            "openid",
            "profile",
            "Calendars.ReadWrite",
            "Mail.Read",
            "MailboxFolder.Read",
        ],
    )

    # initialize server
    mcp = FastMCP(name="Outlook MCP", auth=auth)

    @mcp.resource(
        "config://whoami",
        title="Who Am I",
        description="Information about the logged in user",
    )
    def get_who_am_i(ctx: Context) -> dict:
        token = get_access_token()

        return {
            "azure_id": token.claims.get("sub"),
            "email": token.claims.get("email"),
            "name": token.claims.get("name"),
        }

    @mcp.resource(
        "mail://inbox",
        title="User's Inbox",
    )
    async def get_users_inbox(ctx: Context) -> dict:
        token = get_access_token()
        # Create credentials wrapper
        credentials = TokenCredentials(token.token)
        # Create authentication provider
        client = GraphServiceClient(credentials=credentials)

        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            select=["sender", "subject", "receivedDateTime", "body"], top=50
        )

        request_configuration = RequestConfiguration(
            query_parameters=query_params,
        )
        message_resp = await client.me.messages.get(
            request_configuration=request_configuration
        )

        messages = []
        if message_resp and message_resp.value:
            for msg in message_resp.value:
                messages.append(
                    {
                        "subject": msg.subject,
                        "receieved": msg.received_date_time,
                        "from": msg.from_,
                        # would include body; but it's raw HTML; should parse it as text first
                    }
                )

        return {"messages": messages, "count": len(messages)}

    @mcp.tool("mail-send", description="sends a test email to the user signed in")
    def send_email() -> str:
        return "sent email!"

    # start the server
    mcp.run("streamable-http")


if __name__ == "__main__":
    main()
