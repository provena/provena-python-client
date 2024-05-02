import requests
from typing import Dict, Any

class APIClient:
    def __init__(self):
        self.session = requests.Session()

    
    def get(self, endpoint: str, params: Dict[str, Any] = None, timeout: int = None) -> requests.Response:
        """Sends a GET request to the specified endpoint with the given params

        Parameters
        ----------
        endpoint : str
            _description_
        params : Dict[str, Any], optional
            _description_, by default None

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
            _description_
        data : Dict[str, Any]
            _description_

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
