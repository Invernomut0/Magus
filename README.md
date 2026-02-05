# Magus Conversation Agent

Un custom component per Home Assistant che fornisce un agente conversazionale utilizzando un motore AI simile a GitHub Copilot (basato su OpenAI) per interpretare comandi vocali relativi alla domotica e rispondere tramite Alexa.

## Installazione

1. Copia la cartella `custom_components/magus_conversation_agent` nella directory `custom_components` della tua installazione Home Assistant.

2. Riavvia Home Assistant.

## Configurazione

Aggiungi al tuo `configuration.yaml`:

```yaml
magus_conversation_agent:
  api_key: "your_openai_api_key_here"

conversation:
  - name: Magus Agent
    provider: magus_conversation_agent
```

## Funzionamento

L'agente riceve input vocali, li elabora con l'AI per generare una risposta appropriata, e invia la risposta tramite il servizio `notify.alexa_media_echo_dot_di_lorenzo`.

Nota: Poiché GitHub Copilot non ha un'API pubblica, questo componente utilizza OpenAI come motore AI. Se desideri utilizzare un altro servizio, modifica il codice in `conversation.py`.

## TODO

- Migliorare l'integrazione con comandi domotica effettivi.
- Aggiungere supporto per più servizi di notifica.
- Implementare autenticazione sicura per l'API key.