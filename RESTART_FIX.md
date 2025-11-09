# Fix voor Restart Error - InhouseTrainingPage

## Probleem
Er trad een fout op bij het herstarten van de applicatie vanwege een schema mismatch tussen de database en het InhouseTrainingPage model. Dit kwam doordat migration 0007 nog niet was uitgevoerd terwijl de model definitie al was aangepast.

## Oplossing
De admin.py is aangepast om robuuster om te gaan met deze situatie door een try-except blok toe te voegen aan de `has_add_permission` methode.

## Stappen om het probleem op te lossen:

### 1. Herstart de Docker containers
```bash
docker-compose down
docker-compose up -d
```

### 2. Voer de pending migrations uit
```bash
docker-compose exec web python manage.py migrate
```

### 3. Controleer of alles werkt
```bash
docker-compose logs -f web
```

## Wat is er aangepast?
- **File**: `backend/workshops/admin.py`
- **Wijziging**: De `InhouseTrainingPageAdmin.has_add_permission()` methode heeft nu foutafhandeling om schema mismatches tijdens startup op te vangen.

## Technische details
Het probleem ontstond omdat:
1. Migration 0007 velden verwijdert uit het InhouseTrainingPage model
2. De model definitie in `models.py` komt overeen met de staat **na** de migratie
3. De database was nog in de staat **voor** de migratie
4. Bij startup riep `has_add_permission()` de methode `InhouseTrainingPage.objects.exists()` aan
5. Dit genereerde een SQL query die niet overeen kwam met de database schema
6. Django kon niet opstarten om migrations uit te voeren (chicken-and-egg probleem)

De fix vangt deze fout op, waardoor Django succesvol kan opstarten en migrations kan uitvoeren.
