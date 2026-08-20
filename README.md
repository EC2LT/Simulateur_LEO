

## Installation

Clonez le projet avec la commande suivante :

```bash
git clone https://github.com/mon-compte/mon-projet.git
```

Entrez ensuite dans le dossier :

```bash
cd mon-projet
```

Installez les dépendances :

```bash
pip install -r requirements.txt
```

Téléchargez le TLE

```bash
curl -o data/tle/starlink.txt "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"
```

Lancez finalement l'application :

```bash
python3 main.py
```
