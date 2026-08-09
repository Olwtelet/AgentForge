import json
import os

import httpx
from dotenv import load_dotenv

from shared_functions.base_module import BaseModule

# Private API - needs a token.
# Get one at https://api.metrolisboa.pt/store/apis/info?name=EstadoServicoML&version=1.0.1&provider=admin
# Tokens are short-lived (by default they expire after 3600 seconds).
# Set it in your environment (or .env file) as METRO_API_TOKEN. Never commit real tokens.

load_dotenv()

DEFAULT_TIMEOUT = 15.0


class MetroAPI(BaseModule):

    @staticmethod
    def _headers() -> dict:
        token = os.getenv("METRO_API_TOKEN", "")
        if not token:
            raise RuntimeError(
                "METRO_API_TOKEN is not set. Add it to your environment or .env file. "
                "See the README for how to obtain a token."
            )
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }

    @staticmethod
    def get_state_subway() -> str:
        """
        Useful function to get the information about the state of the subway.
        """
        url = "https://api.metrolisboa.pt:8243/estadoServicoML/1.0.1/estadoLinha/todos"
        try:
            response = httpx.get(url, headers=MetroAPI._headers(), timeout=DEFAULT_TIMEOUT)
        except (RuntimeError, httpx.HTTPError) as exc:
            return f"Failed to get state subway information: {exc}"

        if response.status_code == 200:
            return json.dumps(response.json())
        return f"Failed to get state subway information: {response.status_code}"

    @staticmethod
    def get_times_next_two_subways_in_station(station: str) -> str:
        """
        Useful to get the time (in seconds) of the next two subways in a station.
        """
        url = (
            "https://api.metrolisboa.pt:8243/estadoServicoML/1.0.1/"
            f"tempoEspera/Estacao/{station}"
        )
        try:
            response = httpx.get(url, headers=MetroAPI._headers(), timeout=DEFAULT_TIMEOUT)
        except (RuntimeError, httpx.HTTPError) as exc:
            return f"Failed to get time for the next two subways in station: {exc}"

        if response.status_code == 200:
            data = response.json()
            tempos_chegada = [int(item["tempoChegada1"]) for item in data["resposta"]]
            lowest_tempos = sorted(tempos_chegada)[:2]
            return json.dumps({"times": lowest_tempos, "metric": "seconds"})
        return f"Failed to get time for the next two subways in station: {response.status_code}"
