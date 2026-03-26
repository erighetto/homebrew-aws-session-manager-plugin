Ho letto il repository e ti propongo un **documento di modifiche per Codex** già orientato all’esecuzione. Il punto principale è questo: nel repository attuale il cask e lo script di update sono ancora basati sul **bundled installer `.zip`**, mentre la scelta concordata era usare il **signed installer `.pkg`**. Inoltre la `validate.yml` oggi non fallisce davvero su audit/style perché entrambe le verifiche sono mascherate con `|| true`. ([GitHub][1])

AWS sulla pagina macOS documenta entrambe le strade, ma distingue esplicitamente tra **signed installer (`.pkg`)** e **bundled installer (`.zip`)**; il bundled installer richiede anche Python 3.10+ e installa sotto `/usr/local/sessionmanagerplugin` con symlink in `/usr/local/bin`. Il repository invece dichiara nel README di seguire ancora il “bundled-installer flow”, coerentemente con il cask corrente. ([Documentazione AWS][2])

In più, Homebrew segnala oggi che il cask ufficiale `session-manager-plugin` è **deprecated** con disable date `2026-09-01`, e GitHub Releases dell’upstream AWS mostra una release `1.2.792.0` del `2026-03-17`, coerente con il failure che hai visto in audit per drift di versione. ([Homebrew Formulae][3])

Di seguito trovi il documento da passare a Codex.

---

# Documento di modifiche per Codex — `erighetto/homebrew-aws-session-manager-plugin`

## Obiettivo

Riallineare il tap alla decisione architetturale concordata:

* usare **solo il signed installer `.pkg`** AWS su macOS;
* mantenere **version pinning + SHA256 per architettura**;
* automatizzare il bump versione leggendo una sorgente affidabile AWS/upstream;
* rendere la CI **realmente vincolante**;
* ripulire README e workflow per coerenza operativa.

AWS documenta il flusso `.pkg` firmato come opzione ufficiale per macOS, distinta dal bundled installer `.zip`. ([Documentazione AWS][2])

---

## Stato attuale osservato

1. `Casks/session-manager-plugin.rb` usa ancora gli URL `.zip`:

   * `.../plugin/latest/mac/sessionmanager-bundle.zip`
   * `.../plugin/latest/mac_arm64/sessionmanager-bundle.zip`
     e installa tramite `sessionmanager-bundle/install`. ([GitHub][1])

2. `scripts/update_session_manager_plugin.py` scarica ancora gli zip, verifica il file `sessionmanager-bundle/VERSION` e genera il cask in modalità zip-based. ([GitHub][4])

3. `README.md` dichiara ancora che il tap “follows the AWS macOS bundled-installer flow” e cita il requisito Python 3.10+, che vale per il bundled installer, non per il signed `.pkg` path. ([GitHub][5])

4. `.github/workflows/validate.yml` esegue `brew audit --cask --online` e `brew style --fix`, ma entrambe le linee terminano con `|| true`, quindi la pipeline non protegge davvero il repository. ([GitHub][6])

5. `.github/workflows/update-session-manager-plugin.yml` aggiorna il cask e fa push diretto su `main`, ma non esegue una validazione finale del cask prima del commit/push. ([GitHub][7])

---

## Modifiche richieste

### 1) Convertire il cask da `.zip` a `.pkg`

Riscrivere `Casks/session-manager-plugin.rb` per usare gli URL `.pkg` per entrambe le architetture:

* Intel: `https://s3.amazonaws.com/session-manager-downloads/plugin/<version>/mac/session-manager-plugin.pkg`
* Apple Silicon: `https://s3.amazonaws.com/session-manager-downloads/plugin/<version>/mac_arm64/session-manager-plugin.pkg`

Usare stanzas `on_intel` e `on_arm` con:

* `sha256` specifico per architettura
* `url` specifico per architettura

Usare installazione `pkg "session-manager-plugin.pkg"` invece di `installer script`.

Per la rimozione:

* usare `uninstall pkgutil: ...` **solo se il package id è confermato in modo affidabile**
* altrimenti usare un `uninstall delete:` conservativo per rimuovere:

  * `/usr/local/sessionmanagerplugin`
  * `/usr/local/bin/session-manager-plugin`

Nota: non inventare `pkgutil` id. Verificarlo prima in modo empirico o documentarlo come TODO se non verificabile automaticamente. AWS documenta il comando `sudo installer -pkg session-manager-plugin.pkg -target /` e il symlink manuale verso `/usr/local/bin/session-manager-plugin`. ([Documentazione AWS][2])

### 2) Aggiornare il README per riflettere il flusso `.pkg`

Modificare `README.md` nei seguenti punti:

* sostituire ogni riferimento al “bundled-installer flow” con “signed installer (`.pkg`) flow”
* rimuovere il riferimento al requisito Python 3.10+, che nella documentazione AWS è associato al bundled installer, non al `.pkg`
* specificare chiaramente che il tap segue gli installer macOS firmati AWS
* mantenere la nota che il tool è team-maintained e non ufficiale AWS

Aggiungere una sezione “Why this tap exists” che spieghi in modo sintetico:

* Homebrew core depreca il cask ufficiale
* il team usa Session Manager come componente operativo critico
* questo tap fornisce una distribuzione controllata del plugin AWS per macOS

Questa modifica è necessaria perché il README attuale descrive ancora il flusso zip/Python. ([GitHub][5])

### 3) Riscrivere lo script updater per `.pkg`

Refactor completo di `scripts/update_session_manager_plugin.py`:

#### Nuova logica

* ottenere la versione target da una sorgente affidabile
* per ciascuna architettura (`intel`, `arm64`):

  * scaricare il file `.pkg` versionato
  * calcolare SHA256 del `.pkg`
* generare il cask pinned con URL `.pkg` versionati e SHA specifici

#### Sorgente versione consigliata

Usare come prima scelta una sorgente AWS ufficiale/affidabile o, se più robusta nella pratica, GitHub Releases upstream `aws/session-manager-plugin`, dato che oggi mostra `1.2.792.0`, mentre la pagina AWS release history può avere latenza di aggiornamento o differenze di rendering. In ogni caso, documentare esplicitamente nel codice la gerarchia delle sorgenti. ([Documentazione AWS][8])

#### Comportamento desiderato

* tentare URL versionati `.pkg`
* fallire esplicitamente se uno dei due download non esiste
* non usare più `:latest`
* non usare più `sha256 :no_check` dopo il bootstrap iniziale
* generare Ruby già formattato in modo leggibile e vicino allo stile Homebrew

#### Importante

Eliminare completamente:

* parsing del file `sessionmanager-bundle/VERSION`
* logica zip
* requisito Python nel caveat

---

## 4) Rendere il cask leggibile e brew-friendly

Il file `Casks/session-manager-plugin.rb` non deve più essere generato in una singola riga. Generarlo con formattazione multilinea pulita, ordinamento coerente delle stanzas e struttura idiomatica Homebrew.

Target indicativo:

* `cask "session-manager-plugin" do`
* `version "..."`
* `on_arm do ... end`
* `on_intel do ... end`
* `name`
* `desc`
* `homepage`
* `livecheck do ... end`
* eventuale `depends_on`
* `pkg`
* `uninstall`
* `caveats`
* `end`

Questo serve anche perché nel log precedente `brew style --fix` ha corretto automaticamente il file. ([GitHub][1])

### 5) Sistemare `livecheck`

Aggiungere un `livecheck` block esplicito e coerente con la strategia scelta per la versione.

Requisito:

* non lasciare che Homebrew deduca livecheck in modo ambiguo dagli URL;
* definire una sorgente unica e una regex affidabile.

Se si decide di usare AWS release history:

* usare la pagina release history AWS con regex per `x.y.z.w`

Se si decide di usare GitHub Releases upstream:

* usare la pagina/tag release di `aws/session-manager-plugin`

L’obiettivo è evitare mismatch come quello visto tra `1.2.779.0` nel cask e `1.2.792.0` rilevato in audit. ([Documentazione AWS][8])

---

## 6) Correggere la pipeline di validazione

Riscrivere `.github/workflows/validate.yml`.

### Problemi attuali

* usa `|| true`, quindi non protegge il branch
* usa `brew style --fix`, che modifica il file invece di limitarsi a validarlo
* usa `brew audit --online` sempre, mescolando validazione sintattica con controllo di aggiornamento upstream. ([GitHub][6])

### Nuovo comportamento richiesto

La workflow `validate.yml` deve:

* girare su `macos-latest`
* fare checkout
* tappare il repo locale
* eseguire:

  * `brew style Casks/session-manager-plugin.rb`
  * `brew audit --cask session-manager-plugin`
* opzionalmente, eseguire anche `brew install --cask --formula` non serve; meglio una smoke validation limitata, a meno che non si voglia davvero installare il pkg sul runner

### Regole

* rimuovere tutti i `|| true`
* non usare `--fix` in CI di validazione
* se vuoi tenere un controllo sul drift versione, farlo in una job separata e non come blocco principale del branch

---

## 7) Migliorare la workflow di aggiornamento

Modificare `.github/workflows/update-session-manager-plugin.yml`.

### Stato attuale

* gira su `ubuntu-latest`
* esegue solo lo script Python
* mostra il diff
* committa e pusha direttamente se cambia il cask. ([GitHub][7])

### Nuovo comportamento richiesto

Dopo aver rigenerato il cask:

1. eseguire una validazione del file generato
2. solo se valida, fare commit e push

### Opzioni implementative

**Preferita:**

* far girare l’intera workflow su `macos-latest`
* dopo lo script:

  * `brew tap ...`
  * `brew style Casks/session-manager-plugin.rb`
  * `brew audit --cask session-manager-plugin`

**Alternativa:**

* mantenere update su `ubuntu-latest`
* aggiungere una seconda job `validate-generated-cask` su `macos-latest` dipendente dalla prima
* committare solo se la seconda job passa

### Altri miglioramenti richiesti

* commit message con versione, ad esempio:

  * `chore: update session-manager-plugin to 1.2.792.0`
* valutare PR automatica invece di push diretto su `main` se vuoi governance più robusta

---

## 8) Aggiornare il naming nel comando di tap documentato

Nel README e nelle istruzioni, usare sempre il comando reale del repository:

```bash
brew tap erighetto/homebrew-aws-session-manager-plugin
brew install --cask session-manager-plugin
```

Oggi il repository è pubblicato con quel nome, quindi tutta la documentazione deve essere coerente con esso. ([GitHub][5])

---

## 9) Aggiungere una nota esplicita sul rapporto con AWS

Nel README aggiungere un disclaimer breve:

> This project is not affiliated with or endorsed by Amazon Web Services (AWS).
> It is a public, team-maintained Homebrew tap for distributing the AWS Session Manager plugin on macOS.

Questo è coerente con il fatto che il repo è pubblico e il software upstream è di AWS. L’upstream open source `aws/session-manager-plugin` è pubblicato separatamente da AWS su GitHub con licenza Apache-2.0. ([GitHub][9])

---

## Deliverable attesi da Codex

Codex deve produrre:

1. `Casks/session-manager-plugin.rb` riscritto per `.pkg`
2. `scripts/update_session_manager_plugin.py` rifattorizzato per `.pkg` + SHA versionati
3. `README.md` aggiornato e coerente con `.pkg`
4. `.github/workflows/validate.yml` corretta e realmente bloccante
5. `.github/workflows/update-session-manager-plugin.yml` corretta con validazione post-generation
6. eventuali piccoli aggiustamenti di stile/ordine per conformità Homebrew

---

## Criteri di accettazione

La modifica è accettata solo se:

* il cask non contiene più URL `sessionmanager-bundle.zip`; ([GitHub][1])
* il cask non usa più `installer script` del bundle zip; ([GitHub][1])
* il README non parla più di bundled installer né di Python 3.10 come prerequisito del percorso scelto; ([GitHub][5])
* `validate.yml` non contiene più `|| true`; ([GitHub][6])
* l’update workflow valida il cask generato prima del push; ([GitHub][7])
* il version bump automatico produce un cask pinned e auditabile;
* il repository è coerente con la scelta del signed installer `.pkg` documentata da AWS. ([Documentazione AWS][2])

---

## Nota finale per Codex

Non fare modifiche “minime” solo per far passare l’audit. La richiesta è una **correzione di direzione** del repository: da flow zip/bundled a flow pkg/signed, con CI solida e documentazione coerente.

---



[1]: https://raw.githubusercontent.com/erighetto/homebrew-aws-session-manager-plugin/main/Casks/session-manager-plugin.rb "raw.githubusercontent.com"
[2]: https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-macos-overview.html?utm_source=chatgpt.com "Install the Session Manager plugin on macOS"
[3]: https://formulae.brew.sh/cask/session-manager-plugin?utm_source=chatgpt.com "session-manager-plugin"
[4]: https://raw.githubusercontent.com/erighetto/homebrew-aws-session-manager-plugin/main/scripts/update_session_manager_plugin.py "raw.githubusercontent.com"
[5]: https://github.com/erighetto/homebrew-aws-session-manager-plugin "GitHub - erighetto/homebrew-aws-session-manager-plugin · GitHub"
[6]: https://github.com/erighetto/homebrew-aws-session-manager-plugin/blob/main/.github/workflows/validate.yml "homebrew-aws-session-manager-plugin/.github/workflows/validate.yml at main · erighetto/homebrew-aws-session-manager-plugin · GitHub"
[7]: https://github.com/erighetto/homebrew-aws-session-manager-plugin/blob/main/.github/workflows/update-session-manager-plugin.yml "homebrew-aws-session-manager-plugin/.github/workflows/update-session-manager-plugin.yml at main · erighetto/homebrew-aws-session-manager-plugin · GitHub"
[8]: https://docs.aws.amazon.com/systems-manager/latest/userguide/plugin-version-history.html?utm_source=chatgpt.com "Session Manager plugin latest version and release history"
[9]: https://github.com/aws/session-manager-plugin?utm_source=chatgpt.com "aws/session-manager-plugin: This plugin helps you to use ..."
