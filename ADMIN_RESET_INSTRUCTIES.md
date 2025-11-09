# Admin Wachtwoord Reset Instructies

## Probleem
Je kunt niet meer inloggen op het admin panel via `localhost:8000/admin` met je wachtwoord.

## Oplossing

### Optie 1: Via Docker (Aanbevolen)

Als je Docker gebruikt om het project te draaien, voer dan het volgende commando uit:

```bash
docker exec -it workshop_web python manage.py reset_admin_password --password "ditismijnpaswoord"
```

Dit zal:
- Het wachtwoord van de admin gebruiker resetten naar "ditismijnpaswoord"
- Of een nieuwe admin gebruiker aanmaken als deze niet bestaat

### Optie 2: Aangepast wachtwoord

Als je een ander wachtwoord wilt gebruiken:

```bash
docker exec -it workshop_web python manage.py reset_admin_password --password "jouwnieuwewachtwoord"
```

### Optie 3: Andere gebruikersnaam

Als je admin gebruiker een andere naam heeft:

```bash
docker exec -it workshop_web python manage.py reset_admin_password --username "jouwnaam" --password "jouwwachtwoord"
```

## Verificatie

Na het resetten van het wachtwoord:

1. Ga naar `http://localhost:8000/admin`
2. Log in met:
   - **Gebruikersnaam**: `admin` (of de naam die je hebt opgegeven)
   - **Wachtwoord**: `ditismijnpaswoord` (of het wachtwoord dat je hebt opgegeven)

## Alternatieve methode: Nieuwe superuser aanmaken

Als de bovenstaande methode niet werkt, kun je ook een nieuwe superuser aanmaken:

```bash
docker exec -it workshop_web python manage.py createsuperuser
```

Volg de prompts om een gebruikersnaam, email en wachtwoord in te voeren.

## Troubleshooting

### Docker containers draaien niet

Als je een foutmelding krijgt zoals "No such container", start dan eerst je Docker containers:

```bash
docker-compose up -d
```

### Controleer welke containers draaien

```bash
docker ps
```

Je zou `workshop_web` en `workshop_db` moeten zien in de lijst.
