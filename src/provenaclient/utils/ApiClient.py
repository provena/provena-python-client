import requests
from typing import Dict, Any, Optional

class APIClient:
    session: requests.Session

    def __init__(self) -> None:
        """This is an API Client Class that wraps around the requests library used by auth interface for synchronous requests.
        """
        self.session = requests.Session()
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, timeout: int = 0) -> requests.Response:
        """Sends a GET request to the specified endpoint with the given params

        Parameters
        ----------
        endpoint : str
            A keycloak endpoint that includes the realm name.
        params : Dict[str, Any], optional
            Params passed to the GET request, by default None

        Returns
        -------
        requests.Response
            _description_
        """

        url = endpoint
        try:
            response = self.session.get(url = url, params=params, timeout=timeout)
            return response
        except Exception as e:
            print(f"Error making GET request to {url}: {str(e)}")
            raise


    def post(self, endpoint: str, data: Dict[str, Any]) -> requests.Response:
        """Sends a POST request to the specified endpoint with the given data

        Parameters
        ----------
        endpoint : str
            A keycloak endpoint that includes the realm name.
        data : Dict[str, Any]
            Body field of POST request.

        Returns
        -------
        requests.Response
            _description_
        """

        url = endpoint
        try:
            response = self.session.post(url = url, data=data)
            return response
        except Exception as e:
            print(f"Error making POST request to {url}: {str(e)}")
            raise
