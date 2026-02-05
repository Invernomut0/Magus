"""Conversation agent using GitHub Copilot-like AI for Home Assistant."""

import logging

from homeassistant.components.conversation import ConversationEntity, ConversationInput, ConversationResult
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .copilot import MagusCopilotClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class MagusConversationAgent(ConversationEntity):
    """Conversation agent that uses AI to interpret domotics commands."""

    def __init__(self, hass: HomeAssistant, client: MagusCopilotClient, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.client = client
        self.entry = entry
        self._attr_name = "Magus Agent"
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Magus Copilot Agent",
            manufacturer="GitHub",
            model="Copilot",
        )

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return ["it", "en"]

    async def async_process(self, user_input: ConversationInput) -> ConversationResult:
        """Process user input and return response."""
        _LOGGER.debug("Processing user input: %s", user_input.text)

        try:
            # Use Copilot Client
            reply = await self.client.chat_completion(user_input.text)
        except Exception as e:
            _LOGGER.error("Error calling AI: %s", e)
            reply = "Mi dispiace, c'è stato un errore nel processare il comando con Copilot."

        # Send response via Alexa (keeping original logic)
        try:
            await self.hass.services.async_call(
                "notify",
                "alexa_media_echo_dot_di_lorenzo",
                {"message": reply}
            )
        except Exception as e:
            _LOGGER.warning("Could not send notification to Alexa: %s", e)

        return ConversationResult(response=reply, conversation_id=user_input.conversation_id)