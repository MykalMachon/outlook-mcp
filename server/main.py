from fastmcp import FastMCP
from fastmcp.server.auth.providers.azure import AzureProvider

from datetime import datetime

from os import getenv
from dotenv import load_dotenv

load_dotenv()


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
        "mail://inbox",
        title="User's Inbox",
    )
    def get_current_time() -> str:
        current_time = datetime.now()
        print("fetched current time", current_time)
        return current_time

    @mcp.resource("time://current", title="Current Time")
    def get_users_inbox() -> dict:
        return {}

    @mcp.tool("mail-send", description="sends a test email to the user signed in")
    def send_email() -> str:
        return "sent email!"

    # start the server
    mcp.run("streamable-http")


if __name__ == "__main__":
    main()
