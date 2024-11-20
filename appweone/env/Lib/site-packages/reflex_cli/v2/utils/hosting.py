"""Hosting service related utilities."""

from __future__ import annotations

import contextlib
import enum
import json
import os
import platform
import re
import time
import uuid
import webbrowser
from datetime import datetime, timedelta
from http import HTTPStatus
from importlib import metadata
from typing import List, Optional, Dict, Any

import dateutil.parser
import httpx
import typer
import websockets
from pydantic import BaseModel, Field, ValidationError, root_validator

from reflex_cli.v2.consts import (
    HOSTING_SERVICE,
    TIMEOUT,
    HOSTING_CONFIG_FILE,
    REFLEX_DIR,
    HOSTING_UI,
    AUTH_RETRY_LIMIT,
    AUTH_RETRY_SLEEP_DURATION,
)
import importlib.metadata
from reflex_cli.v2.utils import console
from reflex_cli.v2.utils.dependency import detect_encoding


def get_existing_access_token() -> tuple[str, str]:
    """Fetch the access token from the existing config if applicable.

    Returns:
        The access token and the invitation code.
        If either is not found, return empty string for it instead.
    """
    console.debug("Fetching token from existing config...")
    access_token = invitation_code = ""
    try:
        with open(HOSTING_CONFIG_FILE, "r") as config_file:
            hosting_config = json.load(config_file)
            access_token = hosting_config.get("access_token", "")
            invitation_code = hosting_config.get("code", "")
    except Exception as ex:
        console.debug(f"Unable to fetch token from {HOSTING_CONFIG_FILE} due to: {ex}")
    return access_token, invitation_code


def validate_token(token: str):
    """Validate the token with the control plane.

    Args:
        token: The access token to validate.

    Raises:
        ValueError: if access denied.
        Exception: if runs into timeout, failed requests, unexpected errors. These should be tried again.
    """
    try:
        response = httpx.post(
            f"{HOSTING_SERVICE}/v1/authenticate/me",
            headers=authorization_header(token),
            timeout=TIMEOUT,
        )
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise ValueError
        response.raise_for_status()
    except httpx.RequestError as re:
        console.debug(f"Request to auth server failed due to {re}")
        raise Exception(str(re)) from re
    except httpx.HTTPError as ex:
        console.debug(f"Unable to validate the token due to: {ex}")
        raise Exception("server error") from ex
    except ValueError as ve:
        console.debug(f"Access denied for {token}")
        raise ValueError("access denied") from ve
    except Exception as ex:
        console.debug(f"Unexpected error: {ex}")
        raise Exception("internal errors") from ex


def delete_token_from_config(include_invitation_code: bool = False):
    """Delete the invalid token from the config file if applicable.

    Args:
        include_invitation_code:
            Whether to delete the invitation code as well.
            When user logs out, we delete the invitation code together.
    """
    if os.path.exists(HOSTING_CONFIG_FILE):
        hosting_config = {}
        try:
            with open(HOSTING_CONFIG_FILE, "w") as config_file:
                hosting_config = json.load(config_file)
                del hosting_config["access_token"]
                if include_invitation_code:
                    del hosting_config["code"]
                json.dump(hosting_config, config_file)
        except Exception as ex:
            # Best efforts removing invalid token is OK
            console.debug(
                f"Unable to delete the invalid token from config file, err: {ex}"
            )


def save_token_to_config(token: str, code: str | None = None):
    """Best efforts cache the token, and optionally invitation code to the config file.

    Args:
        token: The access token to save.
        code: The invitation code to save if exists.
    """
    hosting_config: dict[str, str] = {"access_token": token}
    if code:
        hosting_config["code"] = code
    try:
        if not os.path.exists(REFLEX_DIR):
            os.makedirs(REFLEX_DIR)
        with open(HOSTING_CONFIG_FILE, "w") as config_file:
            json.dump(hosting_config, config_file)
    except Exception as ex:
        console.warn(f"Unable to save token to {HOSTING_CONFIG_FILE} due to: {ex}")


def requires_access_token() -> str:
    """Fetch the access token from the existing config if applicable.

    Returns:
        The access token. If not found, return empty string for it instead.
    """
    # Check if the user is authenticated

    access_token, _ = get_existing_access_token()
    if not access_token:
        console.debug("No access token found from the existing config.")

    return access_token


def authenticated_token() -> tuple[str, str]:
    """Fetch the access token from the existing config if applicable and validate it.

    Returns:
        The access token and the invitation code.
        If either is not found, return empty string for it instead.
    """
    # Check if the user is authenticated

    access_token, invitation_code = get_existing_access_token()
    if not access_token:
        console.debug("No access token found from the existing config.")
        access_token = ""
    elif not validate_token_with_retries(access_token):
        access_token = ""

    return access_token, invitation_code


def authorization_header(token: str) -> dict[str, str]:
    """Construct an authorization header with the specified token as bearer token.

    Args:
        token: The access token to use.

    Returns:
        The authorization header in dict format.
    """
    try:
        uuid.UUID(token, version=4)
    except:
        return {"Authorization": f"Bearer {token}"}
    else:
        return {"X-API-TOKEN": token}


def requires_authenticated() -> str:
    """Check if the user is authenticated.

    Returns:
        The validated access token or empty string if not authenticated.
    """
    access_token, invitation_code = authenticated_token()
    if access_token:
        return access_token
    return authenticate_on_browser(invitation_code)


def search_app(app_name: str, project_id: str | None, token: str | None = None) -> dict:
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    if project_id is None:
        project_id = ""
    response = httpx.get(
        HOSTING_SERVICE
        + f"/v1/apps/search?app_name={app_name}&project_id={project_id}",
        headers=authorization_header(token),
        timeout=TIMEOUT,
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        raise Exception(f"deployment failed: {ex_details}")
    response_json = response.json()
    return response_json


def get_app(app_id: str, token: str | None = None) -> dict:
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.get(
        HOSTING_SERVICE + f"/v1/apps/{app_id}",
        headers=authorization_header(token),
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def create_app(
    app_name: str, description: str, project_id: str | None, token: str | None = None
):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.post(
        HOSTING_SERVICE + f"/v1/apps/",
        json={"name": app_name, "description": description, "project": project_id},
        headers=authorization_header(token),
        timeout=TIMEOUT,
    )
    response_json = response.json()
    if response.status_code == HTTPStatus.FORBIDDEN:
        console.debug(f'Server responded with 403: {response_json.get("detail")}')
        raise ValueError(f'{response_json.get("detail", "forbidden")}')
    response.raise_for_status()
    return response_json


def get_hostname(
    app_id: str, app_name: str, hostname: str | None, token: str | None = None
) -> dict:
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")

    data = {"app_id": app_id, "app_name": app_name}
    if hostname:
        clean_hostname = extract_subdomain(hostname)
        if clean_hostname is None:
            raise Exception("bad hostname provided")
        data["hostname"] = clean_hostname
    response = httpx.post(
        HOSTING_SERVICE + f"/v1/apps/reserve",
        headers=authorization_header(token),
        json=data,
        timeout=TIMEOUT,
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        raise Exception(f"deployment failed: {ex_details}")
    response_json = response.json()
    return response_json


def extract_subdomain(url):
    from urllib.parse import urlparse

    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    parsed_url = urlparse(url)
    netloc = parsed_url.netloc

    if netloc.startswith("www."):
        netloc = netloc[4:]

    parts = netloc.split(".")

    if len(parts) >= 2:
        return parts[0]
    elif len(parts) == 1:
        return parts[0]

    return None


def get_secrets(app_id: str, token: str | None = None):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.get(
        HOSTING_SERVICE + f"/v1/apps/{app_id}/secrets",
        headers=authorization_header(token),
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def update_secrets(
    app_id: str, secrets: dict, reboot: bool = False, token: str | None = None
):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.post(
        HOSTING_SERVICE
        + f"/v1/apps/{app_id}/secrets?reboot={"true" if reboot else "false"}",
        headers=authorization_header(token),
        json={"secrets": secrets},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def delete_secret(
    app_id: str, key: str, reboot: bool = False, token: str | None = None
):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.delete(
        HOSTING_SERVICE
        + f"/v1/apps/{app_id}/secrets/{key}?reboot={"true" if reboot else "false"}",
        headers=authorization_header(token),
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def create_project(name: str, token: str | None = None):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.post(
        HOSTING_SERVICE + f"/v1/project/create",
        json={"name": name},
        headers=authorization_header(token),
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def select_project(project: str, token: str | None = None):
    try:
        with open(HOSTING_CONFIG_FILE, "r") as config_file:
            hosting_config = json.load(config_file)
        with open(HOSTING_CONFIG_FILE, "w") as config_file:
            hosting_config["project"] = project
            json.dump(hosting_config, config_file)
    except Exception as ex:
        console.debug(f"Unable to fetch token from {HOSTING_CONFIG_FILE} due to: {ex}")


def get_selected_project() -> str | None:
    try:
        with open(HOSTING_CONFIG_FILE, "r") as config_file:
            hosting_config = json.load(config_file)
            return hosting_config.get("project")
    except Exception as ex:
        console.debug(f"Unable to fetch token from {HOSTING_CONFIG_FILE} due to: {ex}")


def get_projects(token: str | None = None):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.get(
        HOSTING_SERVICE + f"/v1/project/",
        headers=authorization_header(token),
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def get_project_usage(project_id: str, token: str | None = None):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.get(
        HOSTING_SERVICE + f"/v1/project/{project_id}/usage",
        headers=authorization_header(token),
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def get_project_roles(project_id: str, token: str | None = None):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.get(
        HOSTING_SERVICE + f"/v1/project/{project_id}/roles",
        headers=authorization_header(token),
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def get_project_role_permissions(
    project_id: str, role_id: str, token: str | None = None
):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.get(
        HOSTING_SERVICE + f"/v1/project/{project_id}/role/{role_id}",
        headers=authorization_header(token),
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def get_project_role_users(project_id: str, token: str | None = None):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.get(
        HOSTING_SERVICE + f"/v1/project/{project_id}/users",
        headers=authorization_header(token),
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    response_json = response.json()
    return response_json


def invite_user_to_project(role_id: str, user_id: str, token: str | None = None):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.post(
        HOSTING_SERVICE + f"/v1/project/users/invite",
        headers=authorization_header(token),
        json={"user_id": user_id, "role_id": role_id},
        timeout=TIMEOUT,
    )
    response.raise_for_status()


def create_deployment(
    app_name: str,
    project_id: str | None,
    regions: list | None,
    zip_dir: str,
    hostname: str | None,
    vmtype: str | None,
    secrets: dict | None,
    token: str | None = None,
):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    cli_version = importlib.metadata.version("reflex-hosting-cli")
    zips = [
        ("files", ("backend.zip", open(os.path.join(zip_dir, "backend.zip"), "rb"))),
        ("files", ("frontend.zip", open(os.path.join(zip_dir, "frontend.zip"), "rb"))),
    ]
    payload: Dict[str, Any] = {
        "app_name": app_name,
        "reflex_hosting_cli_version": cli_version,
        "reflex_version": "0.6.1",
        "python_version": platform.python_version(),
    }
    if project_id:
        payload["project_id"] = project_id
    if regions:
        regions = regions if regions else []
        payload["regions"] = json.dumps(regions)
    if hostname:
        payload["hostname"] = hostname
    if vmtype:
        payload["vm_type"] = vmtype
    if secrets:
        payload["secrets"] = json.dumps(secrets)

    response = httpx.post(
        HOSTING_SERVICE + f"/v1/deployments",
        data=payload,
        files=zips,
        headers=authorization_header(token),
        timeout=55,
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        try:
            ex_details = ex.response.json().get("detail")
            return f"deployment failed: {ex_details}"
        except:
            return f"deployment failed: internal server error"
    return response.json()


def stop_app(app_id: str, token: str | None = None):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.post(
        HOSTING_SERVICE + f"/v1/apps/{app_id}/stop",
        headers=authorization_header(token),
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        return f"stop app failed: {ex_details}"
    return response.json()


def start_app(app_id: str, token: str | None = None):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.post(
        HOSTING_SERVICE + f"/v1/apps/{app_id}/start",
        headers=authorization_header(token),
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        return f"start app failed: {ex_details}"
    return response.json()


def delete_app(app_id: str, token: str | None = None):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    app = get_app(app_id=app_id)
    if not app:
        console.warn("no app with given id found")
        return
    response = httpx.delete(
        HOSTING_SERVICE + f"/v1/apps/{app["id"]}/delete",
        headers=authorization_header(token),
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        return f"delete app failed: {ex_details}"
    return response.json()


def get_app_logs(
    app_id: str,
    offset: int | None,
    start: int | None,
    end: int | None,
    token: str | None,
):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenicated")
    app = get_app(app_id=app_id)
    if not app:
        console.warn("no app with given id found")
        return
    params = ""
    if offset:
        params = f"?offset={offset}"
    else:
        params = f"?start={start}&end={end}"
    response = httpx.get(
        HOSTING_SERVICE + f"/v1/apps/{app['id']}/logs{params}",
        headers=authorization_header(token),
    )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        return f"get app logs failed: {ex_details}"
    return response.json()


def list_apps(project: str | None = None, token: str | None = None) -> List[dict]:
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    if project:
        url = HOSTING_SERVICE + f"/v1/apps?project={project}"
    else:
        url = HOSTING_SERVICE + f"/v1/apps"

    response = httpx.get(url, headers=authorization_header(token), timeout=5)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as ex:
        ex_details = ex.response.json().get("detail")
        raise Exception(f"list app failed: {ex_details}")
    return response.json()


def get_app_history(app_id: str, token: str | None = None) -> list:
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.get(
        HOSTING_SERVICE + f"/v1/apps/{app_id}/history",
        headers=authorization_header(token),
    )

    response.raise_for_status()
    result = []
    response_json = response.json()
    for deployment in response_json:
        result.append(
            {
                "id": deployment["id"],
                "status": deployment["status"],
                "hostname": deployment["hostname"],
                "python version": deployment["python_version"],
                "reflex version": deployment["reflex_version"],
                "vm type": deployment["vm_type"],
                "timestamp": deployment["timestamp"],
            }
        )
    return result


def get_deployment_status(deployment_id: str, token: str | None = None) -> str:
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.get(
        HOSTING_SERVICE + f"/v1/deployments/{deployment_id}/status",
        headers=authorization_header(token),
    )

    response.raise_for_status()
    return eval(response.text)


def _get_deployment_status(deployment_id: str, token: str) -> str:
    try:
        response = httpx.get(
            HOSTING_SERVICE + f"/v1/deployments/{deployment_id}/status",
            headers=authorization_header(token),
        )
    except:
        return f"lost connection: trying again"

    try:
        response.raise_for_status()
    except:
        return f"error: bad response. recieved a bad response from cloud serivce."
    return eval(response.text)


def watch_deployment_status(deployment_id: str, token: str | None = None):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    with console.status("listening to status updates!"):
        current_status = ""
        while True:
            status = _get_deployment_status(deployment_id=deployment_id, token=token)
            if "completed successfully" in status:
                console.success(status)
                break
            if "build error" in status:
                console.warn(status)
                console.warn(
                    f"to see the build logs:\n reflex apps build-logs {deployment_id}"
                )
                break
            if "error" in status:
                console.warn(status)
                break
            if status == current_status:
                continue
            current_status = status
            console.info(status)
            time.sleep(0.5)
    return False


def get_deployment_build_logs(deployment_id: str, token: str | None = None):
    if not token:
        if not (token := requires_authenticated()):
            raise Exception("not authenticated")
    response = httpx.get(
        HOSTING_SERVICE + f"/v1/deployments/{deployment_id}/build/logs",
        headers=authorization_header(token),
    )

    response.raise_for_status()
    return response.json()


def list_projects():
    pass


def fetch_token(request_id: str) -> tuple[str, str]:
    """Fetch the access token for the request_id from Control Plane.

    Args:
        request_id: The request ID used when the user opens the browser for authentication.

    Returns:
        The access token if it exists, None otherwise.
    """
    access_token = invitation_code = ""
    print(f"{HOSTING_SERVICE}/v1/authenticate/{request_id}")
    try:
        resp = httpx.get(
            f"{HOSTING_SERVICE}/v1/authenticate/{request_id}",
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        access_token = (resp_json := resp.json()).get("access_token", "")
        invitation_code = resp_json.get("code", "")
        project_id = resp_json.get("user_id", "")
        select_project(project=project_id)
    except httpx.RequestError as re:
        console.debug(f"Unable to fetch token due to request error: {re}")
    except httpx.HTTPError as he:
        console.debug(f"Unable to fetch token due to {he}")
    except json.JSONDecodeError as jde:
        console.debug(f"Server did not respond with valid json: {jde}")
    except KeyError as ke:
        console.debug(f"Server response format unexpected: {ke}")
    except Exception:
        console.debug("Unexpected errors: {ex}")

    return access_token, invitation_code


def authenticate_on_browser(invitation_code: str) -> str:
    """Open the browser to authenticate the user.

    Args:
        invitation_code: The invitation code if it exists.

    Returns:
        The access token if valid, empty otherwise.
    """
    console.print(f"Opening {HOSTING_UI} ...")
    request_id = uuid.uuid4().hex
    auth_url = f"{HOSTING_UI}?request-id={request_id}&code={invitation_code}"
    if not webbrowser.open(auth_url):
        console.warn(
            f"Unable to automatically open the browser. Please go to {auth_url} to authenticate."
        )
    access_token = invitation_code = ""
    console.ask("please return after login on webiste complete")
    with console.status("Waiting for access token ..."):
        for _ in range(AUTH_RETRY_LIMIT):
            access_token, invitation_code = fetch_token(request_id)
            if access_token:
                break
            else:
                time.sleep(1)

    if access_token and validate_token_with_retries(access_token):
        save_token_to_config(access_token, invitation_code)
    else:
        access_token = ""
    return access_token


def validate_token_with_retries(access_token: str) -> bool:
    """Validate the access token with retries.

    Args:
        access_token: The access token to validate.

    Returns:
        True if the token is valid,
        False if invalid or unable to validate.
    """
    with console.status("Validating access token ..."):
        for _ in range(AUTH_RETRY_LIMIT):
            try:
                validate_token(access_token)
                return True
            except ValueError:
                console.error(f"Access denied")
                delete_token_from_config()
                break
            except Exception as ex:
                console.debug(f"Unable to validate token due to: {ex}, trying again")
                time.sleep(AUTH_RETRY_SLEEP_DURATION)
    return False


def process_envs(envs: list[str]) -> dict[str, str]:
    """Process the environment variables.

    Args:
        envs: The environment variables expected in key=value format.

    Raises:
        SystemExit: If the envs are not in valid format.

    Returns:
        The processed environment variables in a dict.
    """
    processed_envs = {}
    for env in envs:
        kv = env.split("=", maxsplit=1)
        if len(kv) != 2:
            raise SystemExit("Invalid env format: should be <key>=<value>.")

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", kv[0]):
            raise SystemExit(
                "Invalid env name: should start with a letter or underscore, followed by letters, digits, or underscores."
            )
        processed_envs[kv[0]] = kv[1]
    return processed_envs


def log_out_on_browser():
    """Open the browser to authenticate the user."""
    # Fetching existing invitation code so user sees the log out page without having to enter it
    invitation_code = None
    with contextlib.suppress(Exception):
        _, invitation_code = get_existing_access_token()
        console.debug("Found existing invitation code in config")
        delete_token_from_config()
    console.print(f"Opening {HOSTING_UI} ...")
    if not webbrowser.open(f"{HOSTING_UI}?code={invitation_code}"):
        console.warn(
            f"Unable to open the browser automatically. Please go to {HOSTING_UI} to log out."
        )


def get_vm_types() -> list[dict]:
    try:
        response = httpx.get(
            HOSTING_SERVICE + "/v1/deployments/vm_types",
            timeout=10,
        )
        response.raise_for_status()
        response_json = response.json()
        if response_json is None or not isinstance(response_json, list):
            console.error("Expect server to return a list ")
            return []
        if (
            response_json
            and response_json[0] is not None
            and not isinstance(response_json[0], dict)
        ):
            console.error("Expect return values are dict's")
            return []
        return response_json
    except Exception as ex:
        console.error(f"Unable to get vmtypes due to {ex}.")
        return []


def get_regions() -> list[dict]:
    """Get the supported regions from the hosting server.

    Returns:
        A list of dict representation of the region information.
    """
    try:
        response = httpx.get(
            HOSTING_SERVICE + "/v1/deployments/regions",
            timeout=10,
        )
        response.raise_for_status()
        response_json = response.json()
        if response_json is None or not isinstance(response_json, list):
            console.error("Expect server to return a list ")
            return []
        if (
            response_json
            and response_json[0] is not None
            and not isinstance(response_json[0], dict)
        ):
            console.error("Expect return values are dict's")
            return []
        result = []
        for region in response_json:
            result.append({"name": region["name"], "code": region["code"]})
        return result
    except Exception as ex:
        console.error(f"Unable to get regions due to {ex}.")
        return []
