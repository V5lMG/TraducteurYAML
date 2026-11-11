# Traducteur YAML V2 (EN ➔ FR)

[![Auteur](https://img.shields.io/badge/Auteur-ValMG-blue.svg)](https://github.com/ValMG)
[![Version](https://img.shields.io/badge/Version-2.0.0-green.svg)]()
[![License](https://img.shields.io/badge/Licence-Libre-orange.svg)]()

Traducteur de fichiers YAML (spécialisé pour les fichiers de configuration et de langue Minecraft) développé par **ValMG**, fonctionnant **100% hors-ligne**, sans **aucune dépendance à Google** ni besoin de clé d'API.

---

## 🚀 Nouveautés de la V2

- **Zéro API externe** : Utilise le moteur neuronal local open-source [Argos Translate](https://github.com/argos-translate/argos-translate).
- **Glossaire prioritaire (`dictionary.json`)** : Définissez vos propres correspondances de termes ou lexiques de jeu prioritaires.
- **Préservation intégrale du YAML** :
  - Conserve les commentaires (`#`), l'indentation et les blocs multilignes (`|`).
  - Protège les types natifs (les booléens `true`/`false` et les nombres ne sont pas corrompus).
- **Protection des variables & balises Minecraft** :
  - Variables de substitution : `%player%`, `%money%`, `%kingdoms_bank%`, etc.
  - Balises de style : `{$p}`, `{$e}`, `{$sep}`, codes couleurs `&6`, `&l`, etc.
  - Commandes et actions : `hover:{...}`, `/k claim`, URLs.
  - Identifiants techniques et sons (`BLOCK_NOTE_BLOCK_BELL`, etc.).

---

## 📦 Installation

Nécessite Python 3.10 ou supérieur.

```bash
pip install -r requirements.txt
```

> **Note :** Au tout premier lancement, le modèle de traduction local (~80 Mo) est téléchargé automatiquement une seule fois. Par la suite, l'outil fonctionne **sans aucune connexion Internet**.

---

## 🛠️ Utilisation

### Traduction standard (par défaut `en.yml` ➔ `fr.yml`)
```bash
python main.py
```

### Options en ligne de commande
```bash
python main.py -i mon_fichier_en.yml -o mon_fichier_fr.yml -d dictionary.json
```

| Argument         | Description            | Valeur par défaut |
|:-----------------|:-----------------------|:------------------|
| `-i`, `--input`  | Fichier YAML source    | `en.yml`          |
| `-o`, `--output` | Fichier YAML traduit   | `fr.yml`          |
| `-d`, `--dict`   | Fichier glossaire JSON | `dictionary.json` |
| `--from-lang`    | Code langue source     | `en`              |
| `--to-lang`      | Code langue cible      | `fr`              |

---

## 📖 Guide : Comment obtenir et ajouter un Dictionnaire

Le projet est conçu pour que l'ajout d'un dictionnaire soit **immédiat et sans configuration**.

### Méthode 1 : Téléchargement automatique en 1 clic (Recommandé)
Un script intégré télécharge et compile automatiquement plus de **61 000 mots** issus des bases ouvertes officielles :
```bash
python download_dictionaries.py
```
> **Ce que fait cette commande :**
> - Télécharge les dictionnaires complets du **Wiktionnaire** et de **FreeDict**.
> - Les extrait et les compile directement dans le dossier `dictionaries/`.
> - Fusionne le tout dans `dictionary.json` tout en préservant vos termes de jeu prioritaires.

---

### Méthode 2 : Télécharger un dictionnaire existant sur Internet
Vous pouvez récupérer des dictionnaires bilingues libres en ligne et les déposer directement dans le dossier `dictionaries/` :
- **[Kaikki.org (Wiktionnaire)](https://kaikki.org/dictionary/French/index.html)** : Téléchargez les extraits en JSON/JSONL.
- **[FreeDict](https://freedict.org/downloads/)** : Téléchargez les fichiers `.tei` (ex: `eng-fra.tei`).
- **[Dépôts GitHub](https://github.com/pquentin/wiktionary-translations)** : Fichiers CSV ou TSV de traductions.

Il suffit de **glisser le fichier téléchargé dans le dossier `dictionaries/`**, sans avoir à le renommer ni le convertir.

---

### Méthode 3 : Créer son propre dictionnaire (Personnalisé)
Pour ajouter vos propres mots ou expressions spécifiques (termes de jeu, jargon, etc.), créez simplement un fichier dans `dictionaries/` dans le format de votre choix :

#### Option A : Fichier texte simple (`dictionaries/mon_glossaire.txt`)
```text
warp pad = plaque de téléportation
siege cannon = canon de siège
damage boost: augmentation des dégâts
dragon egg -> œuf de dragon
```

#### Option B : Fichier JSON (`dictionaries/mon_lexique.json`)
```json
{
  "outpost": "avant-poste",
  "turret": "tourelle",
  "resource points": "points de ressources"
}
```

#### Option C : Fichier CSV / Excel (`dictionaries/termes.csv`)
```csv
kingdom;royaume
ranks;rangs
nexus;nexus
```

---

### ⚙️ Prise en compte et Priorité
Dès que vous lancez `python main.py` :
1. **Détection automatique** : Le terminal confirme le chargement de vos fichiers :
   ```text
   [Dictionnaires] 61,096 mots chargés depuis 4 fichier(s).
   ```
2. **Priorité absolue** : Si un terme est présent dans [`dictionary.json`](file:///E:/2%20-%20PYTHON/TraducteurYAML/dictionary.json) à la racine, sa traduction écrase toujours les définitions génériques des autres dictionnaires.

---

## 📂 Structure du Projet

```text
TraducteurYAML/
│
├── main.py                   # Point d'entrée CLI
├── translator.py             # Moteur de traduction locale, n-grammes et protection des balises
├── yaml_processor.py         # Lecteur/Écripteur YAML préservant les structures
├── download_dictionaries.py  # Script de téléchargement et compilation des dictionnaires
├── dictionary.json           # Dictionnaire complet compilé (61 000+ mots)
├── dictionaries/             # Fichiers bruts et exports complets
│   ├── wiktionary_raw.csv
│   ├── freedict_raw.tei
│   └── en_fr_full.json
├── requirements.txt          # Dépendances Python
└── README.md                 # Documentation
```

---

## 👤 Auteur

- **Auteur** : ValMG
- **Projet** : Traducteur YAML V2 (Hors-ligne / Dictionnaires + IA locale)

