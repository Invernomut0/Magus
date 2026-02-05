"""Magus Conversation Agent for Home Assistant."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .conversation import MagusConversationAgent
from .copilot import MagusCopilotClient
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Magus Conversation Agent component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Magus from a config entry."""
    access_token = entry.data["access_token"]
    notify_entity = entry.data.get("notify_entity", "media_player.alexa_media_echo_dot_di_lorenzo")
    session = async_get_clientsession(hass)
    
    client = MagusCopilotClient(session, access_token=access_token)
    
    agent = MagusConversationAgent(hass, client, entry, notify_entity)
    
    from homeassistant.components.conversation import async_set_agent
    await async_set_agent(hass, entry, agent)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    from homeassistant.components.conversation import async_unset_agent
    async_unset_agent(hass, entry)
    return True