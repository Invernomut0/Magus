# Magus Conversation Agent

# Magus Conversation Agent

Un custom component per Home Assistant che fornisce un agente conversazionale utilizzando GitHub Copilot per interpretare comandi vocali relativi alla domotica.

## Installazione

**Tramite HACS (consigliato):**
1.  Aggiungi questo repository come Custom Repository in HACS.
2.  Cerca "Magus Conversation Agent" e installa.
3.  Riavvia Home Assistant.

**Manuale:**
1.  Copia la cartella `custom_components/magus_conversation_agent` nella directory `custom_components` della tua installazione Home Assistant.
2.  Riavvia Home Assistant.

## Configurazione

1.  Vai in **Impostazioni** -> **Dispositivi e Servizi**.
2.  Clicca su **+ AGGIUNGI INTEGRAZIONE**.
3.  Cerca **Magus Conversation Agent**.
4.  Segui le istruzioni a schermo per autenticarti con GitHub (Device Flow).
5.  Seleziona l'entità di notifica (es. Alexa) per le risposte vocali.

## Funzionamento

L'agente utilizza l'API di GitHub Copilot (emulando VS Code) per processare le richieste. Le risposte vengono inviate al servizio di notifica configurato.

## Note

Questo componente richiede un abbonamento attivo a GitHub Copilot.