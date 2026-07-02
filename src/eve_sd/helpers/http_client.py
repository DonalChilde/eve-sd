"""HTTP client factory helpers for eve-sd network calls.

These helpers return preconfigured ``httpx2`` clients that include the
project's default User-Agent header unless explicitly overridden.
"""

from httpx2 import AsyncClient, Client

from eve_sd import USER_AGENT


def config_http_client(user_agent: str | None = None) -> Client:
    """Create a synchronous HTTP client with a User-Agent header.

    Args:
        user_agent: Optional custom User-Agent header value.

    Returns:
        Configured synchronous ``httpx2.Client`` instance.

    Notes:
        The caller owns the returned client and is responsible for closing it.
    """
    if user_agent is None:
        user_agent = USER_AGENT
    return Client(headers={"User-Agent": user_agent})


async def config_async_http_client(user_agent: str | None = None) -> AsyncClient:
    """Create an asynchronous HTTP client with a User-Agent header.

    Args:
        user_agent: Optional custom User-Agent header value.

    Returns:
        Configured asynchronous ``httpx2.AsyncClient`` instance.

    Notes:
        The caller owns the returned client and is responsible for closing it.
    """
    if user_agent is None:
        user_agent = USER_AGENT
    return AsyncClient(headers={"User-Agent": user_agent})
