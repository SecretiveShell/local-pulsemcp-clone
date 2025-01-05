# Local PulseMCP Clone

This is a local clone of the PulseMCP API repository. It is intended to be used for development and testing purposes.

## Installation

1. Clone the repository: `git clone https://github.com/SecretiveShell/local-pulsemcp-clone.git`
2. Navigate to the cloned directory: `cd local-pulsemcp-clone`
3. Install the required dependencies: `uv sync`
4. Start the API server: `uv run src/main.py`

## Usage

The API server is now running on `http://localhost:7890`. You can use the following endpoints to interact with the API:

- `GET /integrations`: Fetch a list of integrations from the database.
- `GET /servers`: Fetch a paginated list of servers from the database.
- `POST /download`: Download all PulseMCP data and save it to a SQLite database.

Make sure to access the swagger documentation at `http://localhost:7890/docs` and run the download endpoint to populate the initial database.

## Database

The database is stored in the `pulsemcp.db` file in the root directory of the project. This is created automatically when you use the `POST /download` endpoint.

## License

This project is licensed under the MIT License.