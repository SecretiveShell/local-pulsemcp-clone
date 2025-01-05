from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException
from database import Base, Server, Integration, ServerIntegration
import httpx
import asyncio

# API base URL
BASE_URL = "https://api.pulsemcp.com/v0beta"
DEFAULT_DB_PATH = "pulsemcp.db"

router = APIRouter()

async def fetch_data(client: httpx.AsyncClient, url: str, params: dict = None, error_message: str = "Failed to fetch data"):
    """
    Helper function to fetch data from a given URL with error handling.
    
    Args:
        client: The HTTP client instance.
        url: The API endpoint URL.
        params: Optional query parameters for the request.
        error_message: Error message to raise on failure.

    Returns:
        JSON-decoded response data.

    Raises:
        HTTPException: If the response status code is not 200.
    """
    response = await client.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"{error_message}: {response.text}")
    return response.json()

async def fetch_integrations(client: httpx.AsyncClient):
    """
    Fetch all integrations from the API.

    Args:
        client: The HTTP client instance.

    Returns:
        List of integrations.
    """
    print("Fetching integrations...")
    data = await fetch_data(client, f"{BASE_URL}/integrations", error_message="Failed to fetch integrations")
    return data if isinstance(data, list) else data.get("integrations", [])

async def fetch_servers(client: httpx.AsyncClient, count_per_page: int = 5000):
    """
    Fetch all servers from the API, handling pagination.

    Args:
        client: The HTTP client instance.
        count_per_page: Number of items per page for pagination.

    Returns:
        List of servers.
    """
    print("Fetching servers...")
    servers = []
    offset = 0

    while True:
        params = {"offset": offset, "count_per_page": count_per_page}
        data = await fetch_data(client, f"{BASE_URL}/servers", params=params, error_message="Failed to fetch servers")
        servers.extend(data.get("servers", []))

        if not data.get("next"):
            break

        offset += count_per_page
        await asyncio.sleep(0.2)  # Rate limiting

    return servers

def save_to_database(engine, integrations, servers):
    """
    Save integrations and servers data to the database.

    Args:
        engine: SQLAlchemy engine instance.
        integrations: List of integration data.
        servers: List of server data.
    """
    with Session(engine) as session:
        # Store integrations
        for integration_data in integrations:
            integration = Integration(
                name=integration_data.get("name"),
                slug=integration_data.get("slug"),
                url=integration_data.get("url")
            )
            session.merge(integration)

        # Store servers and their integrations
        for server_data in servers:
            server = Server(
                name=server_data.get("name"),
                url=server_data.get("url"),
                external_url=server_data.get("external_url"),
                short_description=server_data.get("short_description"),
                source_code_url=server_data.get("source_code_url"),
                github_stars=server_data.get("github_stars"),
                package_registry=server_data.get("package_registry"),
                package_name=server_data.get("package_name"),
                package_download_count=server_data.get("package_download_count"),
                experimental_ai_generated_description=server_data.get("EXPERIMENTAL_ai_generated_description"),
                integrations=[
                    ServerIntegration(integration_slug=integration.get("slug"))
                    for integration in server_data.get("integrations", [])
                ]
            )
            session.merge(server)

        session.commit()

@router.post("/download")
async def download_pulsemcp_db():
    """
    Download all PulseMCP data and save it to a SQLite database.

    Returns:
        A success message upon completion.
    """
    print("Starting database download...")

    # Create/connect to database
    engine = create_engine(f"sqlite:///{DEFAULT_DB_PATH}")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    async with httpx.AsyncClient() as client:
        integrations = await fetch_integrations(client)
        servers = await fetch_servers(client)

    print(f"Fetched {len(integrations)} integrations and {len(servers)} servers.")

    save_to_database(engine, integrations, servers)

    print(f"Database saved to {DEFAULT_DB_PATH}.")
    return {"message": f"Database successfully saved to {DEFAULT_DB_PATH}."}
