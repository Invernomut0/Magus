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

    def __init__(self, hass: HomeAssistant, client: MagusCopilotClient, entry: ConfigEntry, notify_entity: str) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.client = client
        self.entry = entry
        self.notify_entity = notify_entity
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

        # Send response via Alexa (or other notify entity)
        try:
            domain = self.notify_entity.split(".")[0]
            service = "notify" if domain == "notify" else "play_media" # naive check, improved below
            
            # Better dispatch based on domain
            if domain == "media_player":
                await self.hass.services.async_call(
                    "notify", 
                    "alexa_media", 
                    {"message": reply, "target": [self.notify_entity], "data": {"type": "tts"}}
                )
            elif domain == "notify":
                 # Remove "notify." prefix for service call
                service_name = self.notify_entity.replace("notify.", "")
                await self.hass.services.async_call(
                    "notify",
                    service_name,
                    {"message": reply}
                )
            else:
                 # Fallback to Alexa Media Player specific call from original code style if it matches
                 # But since we made it generic, let's try to retain the original logic for "alexa_media_echo_dot..." 
                 # which is actually a notify service created by alexa_media_player.
                 # The user selected an entity. If it is a media_player, we might want to TTS to it.
                 # If it is a notify entity, we just send message.
                 
                 # The original code used:
                 # await self.hass.services.async_call("notify", "alexa_media_echo_dot_di_lorenzo", {"message": reply})
                 # This implies "notify.alexa_media_echo_dot_di_lorenzo" exists.
                 
                 # Let's assume the user picks a notify entity or we try to find the notify service for it.
                 pass

        except Exception as e:
            _LOGGER.warning("Could not send notification: %s", e)

        return ConversationResult(response=reply, conversation_id=user_input.conversation_id)