

## Installation

Clonez le projet avec la commande suivante :

```bash
git clone https://github.com/EC2LT/Simulateur_LEO.git
```

Entrez ensuite dans le dossier :

```bash
cd Simulateur_LEO
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
