"""Define the Gazpar API."""
import aiohttp
import async_timeout
from .const import  LOGGER
from typing import Any
import socket
from yarl import URL

SESSION_TOKEN_URL = "https://connexion.grdf.fr/api/v1/authn"
AUTH_TOKEN_URL = "https://connexion.grdf.fr/login/sessionCookieRedirect"

class GazparApiClientError(Exception):
    """Exception to indicate a general API error."""


class GazparApiClientCommunicationError(
    GazparApiClientError,
):
    """Exception to indicate a communication error."""


class GazparApiClientAuthenticationError(
    GazparApiClientError,
):
    """Exception to indicate an authentication error."""
def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise GazparApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()
class  WebLoginSource():

    # ------------------------------------------------------
    def __init__(self, username: str, password: str,  session: aiohttp.ClientSession):

        self.__username = username
        self.__password = password
        self._session = session

    # ------------------------------------------------------
    async def _login(self) -> str:

        response=await self._api_wrapper(
            method="post",
            url=SESSION_TOKEN_URL,
            headers={"Content-type": "application/json", "domain":"grdf.fr","X-Requested-With": "XMLHttpRequest"},
            data={"username": self.__username,"password": self.__password,"options": {"multiOptionalFactorEnroll": "false","warnBeforePasswordExpired": "false"}},

        )
        session_token = response.get("sessionToken")
        LOGGER.debug("Session token: %s", session_token)
        response=await self._api_wrapper(
            method="get",
            url=AUTH_TOKEN_URL,
            headers={"Content-type": "application/json","X-Requested-With": "XMLHttpRequest"},
            params={"checkAccountSetupComplete": "true","token": session_token,"redirectUrl": "https://monespace.grdf.fr"},
            decodeJSON=False

        )
       
        auth_token = self._session.cookie_jar.filter_cookies(URL("https://monespace.grdf.fr")).get("auth_token")


        return auth_token  # type: ignore
    
    async def async_get_data(self) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="get",
            url="https://jsonplaceholder.typicode.com/posts/1",
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        decodeJSON: bool = True,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                )
                _verify_response_or_raise(response)
                if(decodeJSON):
                    return await response.json()
                else:
                    return await response.text()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise GazparApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise GazparApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise GazparApiClientError(
                msg,
            ) from exception