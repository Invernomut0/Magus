"""Config flow for Magus Conversation Agent."""
import logging
from typing import Any, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .copilot import MagusCopilotClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({})

class MagusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Magus Conversation Agent."""

    VERSION = 1

    def __init__(self):
        """Initialize the flow."""
        self._device_code_data = None
        self._client = None

    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        return await self.async_step_device_auth()

    async def async_step_device_auth(self, user_input: Optional[dict[str, Any]] = None) -> FlowResult:
        """Handle device authentication step."""
        errors = {}
        
        if not self._client:
             session = async_get_clientsession(self.hass)
             self._client = MagusCopilotClient(session)

        if user_input is None:
            # First time entry, request device code
            try:
                self._device_code_data = await self._client.request_device_code()
            except Exception as e:
                 _LOGGER.error("Failed to get device code: %s", e)
                 return self.async_abort(reason="connection_error")

        else:
            # User clicked Submit, check for token
            # We use the polling function but effectively just checking once 
            # or we could do a short poll. 
            # Since the user clicked "Submit", they should have approved it.
            # We pass a short expiration to poll_for_token to avoid blocking too long if incomplete.
            
            try:
                access_token = await self._client.poll_for_token(
                    self._device_code_data["device_code"],
                    interval=self._device_code_data["interval"],
                    expires_in=5 # Try for 5 seconds
                )
                
                if access_token:
                    return self.async_create_entry(
                        title="Magus Copilot",
                        data={"access_token": access_token}
                    )
                else:
                    errors["base"] = "authorization_pending"
            except Exception as e:
                _LOGGER.error("Error Checking token: %s", e)
                errors["base"] = "unknown_error"

        # Show the form with the code
        return self.async_show_form(
            step_id="device_auth",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "user_code": self._device_code_data["user_code"],
                "verification_uri": self._device_code_data["verification_uri"],
            },
        )
