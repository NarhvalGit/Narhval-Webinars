# 🎯 Webinar Platform Migratie - Uitvoer Instructies

## Status: ✅ Bestanden klaar voor migratie

Alle benodigde bestanden zijn aangepast en klaar. Volg deze stappen om de migratie uit te voeren:

---

## 📋 Checklist - Wat is aangepast:

- ✅ **models.py** - Workshop → Webinar terminologie + meeting URL velden
- ✅ **admin.py** - Admin interface aangepast voor webinars
- ✅ **populate_data.py** - Test data generator met Teams URLs
- ✅ **0005_webinar_conversion.py** - Nieuwe database migratie
- ✅ **Backups gemaakt** in `backend/workshops/backup_before_webinar/`

---

## 🚀 Stap voor Stap Uitvoering

### Stap 1: Backup Database (BELANGRIJK!)

```bash
# Open PowerShell in project directory
cd C:\Projects\workshop-platform

# Start database container als die nog niet draait
docker-compose up -d db

# Maak database backup
docker-compose exec db pg_dump -U workshop_user workshop_db > backup_voor_webinar_$(Get-Date -Format "yyyyMMdd_HHmmss").sql

# Controleer of backup bestand is aangemaakt
ls backup_voor_webinar_*.sql
```

### Stap 2: Voer Migratie Uit

```bash
# Start alle containers
docker-compose up -d

# Wacht even tot containers klaar zijn (5-10 seconden)
Start-Sleep -Seconds 10

# Voer de migratie uit
docker-compose exec web python manage.py migrate

# Verwachte output:
# Running migrations:
#   Applying workshops.0005_webinar_conversion... OK
```

### Stap 3: Verifieer Migratie

```bash
# Check of migratie succesvol was
docker-compose exec web python manage.py showmigrations workshops

# Verwachte output (alle migrations met [X]):
# workshops
#  [X] 0001_initial
#  [X] 0002_remove_workshop_created_by
#  [X] 0003_category_icon
#  [X] 0004_newslettersubscriber
#  [X] 0005_webinar_conversion
```

### Stap 4: Verwijder Oude Test Data (Optioneel)

```bash
# Open Django shell
docker-compose exec web python manage.py shell

# Voer uit in de shell:
from workshops.models import Workshop, Booking, Review
Review.objects.all().delete()
Booking.objects.all().delete()
Workshop.objects.all().delete()
exit()
```

### Stap 5: Laad Nieuwe Webinar Test Data

```bash
# Genereer nieuwe test data met Teams URLs
docker-compose exec web python manage.py populate_data

# Verwachte output:
# 🚀 Start met GenAI webinars genereren...
# 📁 Categorieën aanmaken...
# 👥 Users aanmaken...
# 🎓 Webinars aanmaken...
# 📅 Boekingen aanmaken...
# ⭐ Reviews aanmaken...
# ✅ Klaar! GenAI webinars succesvol aangemaakt!
```

### Stap 6: Verifieer in Admin Panel

```bash
# Open browser
Start-Process "http://localhost:8000/admin/"

# Login met:
# Username: admin
# Password: ditismijnpaswoord
```

**Check in admin panel:**
- ✅ "Webinars" zichtbaar (niet "Workshops")
- ✅ Meeting URL veld aanwezig
- ✅ Meeting ID en wachtwoord velden zichtbaar
- ✅ Geen locatie/adres/stad velden meer
- ✅ Test data correct met Teams URLs
- ✅ Boekingen tonen "Webinar" label

---

## 🔍 Wat te Controleren

### In Admin Panel:

1. **Webinars lijst:**
   - Kolom "Meeting" moet groene ✓ tonen voor alle webinars
   - Geen "Locatie" kolom meer
   
2. **Webinar detail pagina:**
   - Sectie "Online Meeting Details" zichtbaar
   - Meeting URL veld gevuld
   - Meeting ID veld gevuld
   - Geen locatie/adres/stad velden

3. **Boekingen:**
   - Label "Webinar" in plaats van "Workshop"
   - Alle bestaande boekingen nog steeds werkend

4. **Test data:**
   - Webinars hebben realistische Teams URLs
   - Meeting IDs in format "xxx xxx xxx"
   - Meeting passwords in format "WBxxxx"

---

## ⚠️ Troubleshooting

### Als migratie faalt:

```bash
# Stop containers
docker-compose down

# Herstel database backup
docker-compose up -d db
Get-Content backup_voor_webinar_YYYYMMDD_HHMMSS.sql | docker-compose exec -T db psql -U workshop_user workshop_db

# Check database
docker-compose exec db psql -U workshop_user workshop_db -c "\d workshops_workshop"
```

### Als velden niet kloppen:

```bash
# Check welke velden er zijn
docker-compose exec web python manage.py shell

# In shell:
from workshops.models import Workshop
print([f.name for f in Workshop._meta.fields])
exit()

# Verwacht: meeting_url, meeting_id, meeting_password aanwezig
# Verwacht NIET: location, address, city
```

### Als admin panel errors geeft:

```bash
# Restart web container
docker-compose restart web

# Check logs
docker-compose logs -f web

# Clear Python cache
docker-compose exec web find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
docker-compose restart web
```

---

## 📊 Verwachte Resultaten

Na succesvolle migratie heb je:

- ✅ 7 categorieën (AI Geletterdheid, Prompt Engineering, etc.)
- ✅ 11 webinars (allemaal online via Teams)
- ✅ 6 test users
- ✅ 40-50 boekingen
- ✅ 8-10 reviews

Alle webinars hebben:
- ✅ Teams meeting URL (https://teams.microsoft.com/...)
- ✅ Meeting ID (xxx xxx xxx format)
- ✅ Meeting wachtwoord (WBxxxx format)
- ✅ Hogere max deelnemers (30-50 ipv 15-20)

---

## 🎉 Klaar voor Gebruik

Na succesvolle migratie kun je:

1. **Webinars beheren** via admin panel
2. **Boekingen aanmaken** voor online sessies
3. **Teams links** automatisch aan deelnemers sturen (feature voor later)
4. **Verder met Stap 4** - Frontend templates maken

---

## 📞 Belangrijke Opmerkingen

- 🔴 **Booking reference blijft "WB"** (Webinar Booking) voor NIEUWE boekingen
- 🟡 **Oude boekingen** houden "WS" prefix (geen probleem)
- 🟢 **Database naam** blijft `workshop_db` (geen probleem, is alleen een naam)
- 🟢 **App naam** blijft `workshops` (bevat nu webinars)

---

## ✅ Success Criteria

Migratie is succesvol als:

- [ ] Admin panel toont "Webinars" ipv "Workshops"
- [ ] Meeting URL velden zichtbaar en gevuld
- [ ] Geen locatie velden meer zichtbaar
- [ ] Test data correct geladen
- [ ] Boekingen werken nog steeds
- [ ] Geen errors in logs

---

**Datum:** 2 november 2025  
**Status:** Klaar voor uitvoering  
**Geschatte tijd:** 5-10 minuten

Succes met de migratie! 🚀
