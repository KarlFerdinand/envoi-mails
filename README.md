# envoi-mails

Boîte d'envoi des mails automatiques d'Ivan (newsletter « Tendances marchés », etc.).

1. Une tâche planifiée Claude dépose un fichier `outbox/<nom>-AAAA-MM-JJ.html` et le pousse sur `main`.
2. Le workflow **Envoi mails** l'envoie aussitôt depuis le compte Gmail configuré :
   - objet = balise `<title>` ;
   - destinataires = `<meta name="to" content="...">`, par défaut ivan.vollet@gmail.com ;
   - seules les adresses de `LISTE_AUTORISEE` (dans `scripts/envoyer.py`) sont acceptées.
3. En cas d'échec, GitHub t'envoie un mail « Run failed ».
4. Pour renvoyer une lettre : Actions → Envoi mails → Run workflow → `outbox/<fichier>.html`.

Secrets requis (Settings → Secrets and variables → Actions → New repository secret) :
- `GMAIL_USER` : karlf.braun@gmail.com
- `GMAIL_APP_PASSWORD` : mot de passe d'application Gmail (16 caractères)
