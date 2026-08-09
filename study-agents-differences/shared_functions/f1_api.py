import json

import httpx

from shared_functions.base_module import BaseModule

# Public API

DEFAULT_TIMEOUT = 15.0


class F1API(BaseModule):

    @staticmethod
    def get_driver_info(driver_number: int, session_key: int = 9158) -> str:
        """
        Useful function to get F1 driver information.
        """
        url = (
            "https://api.openf1.org/v1/drivers"
            f"?driver_number={driver_number}&session_key={session_key}"
        )
        try:
            response = httpx.get(url, timeout=DEFAULT_TIMEOUT)
        except httpx.HTTPError as exc:
            return f"Failed to get driver information: {exc}"

        if response.status_code == 200:
            return json.dumps(response.json())
        return f"Failed to get driver information: {response.status_code}"
