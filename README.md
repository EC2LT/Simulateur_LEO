

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

## Image de simulation

Logs
<img width="605" height="317" alt="image" src="https://github.com/user-attachments/assets/f3f989b5-edc4-4e18-8556-fff2aa6baa80" />


Interface
<img width="1782" height="749" alt="image" src="https://github.com/user-attachments/assets/c11fdce6-3c0a-4dea-9347-abbcedec7472" />
