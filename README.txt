ESECUZIONE SERVER
Una volta posizionati nella cartella "codice/", server.py è eseguibile semplicemente tramite il comando "python server.py".
server.py prevede anche un parametro "flushstats" (non obbligatorio) che indica al server di pulire le statistiche relative alle giocate/vittorie fino a quel momento all'inizio della sua esecuzione. In questo caso il server è eseguibile con "python server.py flushstats".

ESECUZIONE CLIENT
Una volta posizionati nella cartella "codice/" ed avviato il server, un client può essere eseguito semplicemente tramite "python client.py"

ESECUZIONE TEST
Una volta posizionati nella cartella "codice/" è necessario prima di eseguire i test lanciare il server tramite "python server.py flushstats".
Una volta lanciato il server, in un nuovo terminale posizionarsi nella cartella "codice/test". Da qui eseguire i seguenti comandi in ordine:
- python test_step1.py
- python test_step2.py
- python test_step3.py
- python test_step4.py
- python test_step5.py