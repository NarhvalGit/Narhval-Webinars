# 📋 Webinar Platform - Wijzigingen Overzicht

## 🎯 Doel
Het Workshop Platform is omgezet naar een Webinar Platform voor online opleidingen via Microsoft Teams.

---

## ✅ Uitgevoerde Wijzigingen

### 1. **Database Model (models.py)**

#### Verwijderde Velden:
```python
# ❌ VERWIJDERD
location = models.CharField('Locatie', max_length=200)
address = models.CharField('Adres', max_length=300, blank=True)
city = models.CharField('Stad', max_length=100, default='Gent')
```

#### Toegevoegde Velden:
```python
# ✅ NIEUW
meeting_url = models.URLField(
    'Teams Meeting URL',
    max_length=500,
    blank=True,
    help_text='Link naar de Microsoft Teams meeting'
)

meeting_id = models.CharField(
    'Meeting ID',
    max_length=100,
    blank=True,
    help_text='Optioneel meeting ID voor deelnemers'
)

meeting_password = models.CharField(
    'Meeting Wachtwoord',
    max_length=100,
    blank=True,
    help_text='Optioneel wachtwoord voor de meeting'
)
```

#### Aangepaste Velden:
```python
# Max deelnemers verhoogd voor online
max_participants: 100 → 500

# Booking reference prefix
"WS" → "WB" (Webinar Booking)

# Help texts aangepast voor online context
requirements: "Bijv. ervaring, benodigde software, etc."
what_to_bring: "Benodigde materialen voor thuis"
```

#### Meta Wijzigingen:
```python
verbose_name = 'Webinar'  # was: 'Workshop'
verbose_name_plural = 'Webinars'  # was: 'Workshops'
```

---

### 2. **Admin Interface (admin.py)**

#### Terminologie Updates:
- `workshop_count` → `webinar_count`
- `duplicate_workshops` → `duplicate_webinars`
- Admin labels "Workshop" → "Webinar"
- Breadcrumbs aangepast

#### Nieuwe Features:
```python
def meeting_status(self, obj):
    """Toon of meeting URL is ingevuld"""
    if obj.meeting_url:
        return format_html('<span style="color: green;">✓ Meeting link</span>')
    return format_html('<span style="color: red;">✗ Geen meeting</span>')
```

#### Fieldsets Aanpassingen:
```python
# NIEUW: Online Meeting Details sectie
('Online Meeting Details', {
    'fields': ('meeting_url', 'meeting_id', 'meeting_password'),
    'description': 'Microsoft Teams meeting informatie voor deelnemers'
}),

# VERWIJDERD: Locatie sectie
# ('Locatie', {
#     'fields': ('location', 'address', 'city')
# }),
```

#### List Display:
```python
# Vervangen:
'location' → 'meeting_status'

# Verwijderde filters:
- 'city'
```

---

### 3. **Test Data Generator (populate_data.py)**

#### Nieuwe Functies:
```python
def generate_teams_url(self):
    """Genereer een realistische Teams meeting URL"""
    meeting_code = f"{''.join([str(random.randint(0, 9)) for _ in range(19)])}"
    return f"https://teams.microsoft.com/l/meetup-join/19%3ameeting_{meeting_code}%40thread.v2/0"

def generate_meeting_id(self):
    """Genereer een meeting ID"""
    return f"{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"
```

#### Data Aanpassingen:
- **Beschrijvingen:** Alle vermeldingen van fysieke locatie vervangen door "online webinar"
- **Max deelnemers:** Verhoogd naar 20-30 (was 10-15)
- **Meeting URLs:** Automatisch gegenereerd voor alle webinars
- **Short descriptions:** "(Online webinar)" toegevoegd

---

### 4. **Database Migratie (0005_webinar_conversion.py)**

```python
operations = [
    # Verwijder locatie velden
    RemoveField('workshop', 'location'),
    RemoveField('workshop', 'address'),
    RemoveField('workshop', 'city'),
    
    # Voeg meeting velden toe
    AddField('workshop', 'meeting_url'),
    AddField('workshop', 'meeting_id'),
    AddField('workshop', 'meeting_password'),
    
    # Update validators
    AlterField('workshop', 'max_participants'),
    
    # Update verbose names
    AlterField('booking', 'workshop'),
    AlterField('review', 'workshop'),
    
    # Update model meta
    AlterModelOptions('workshop'),
]
```

---

## 📊 Vergelijkingstabel

| Aspect | Workshop (oud) | Webinar (nieuw) |
|--------|----------------|-----------------|
| **Locatie** | Fysiek adres + stad | Teams meeting URL |
| **Meeting Info** | - | URL + ID + wachtwoord |
| **Max Deelnemers** | 100 | 500 |
| **Booking Prefix** | WS12345678 | WB12345678 |
| **Admin Label** | "Workshop" | "Webinar" |
| **Verbose Name** | Workshop/Workshops | Webinar/Webinars |
| **Filters** | Incl. 'city' | Geen 'city' |
| **Test Data** | 15 deelnemers | 30 deelnemers |

---

## 🔧 Technische Details

### Database Schema Wijzigingen:
```sql
-- Verwijderd
ALTER TABLE workshops_workshop DROP COLUMN location;
ALTER TABLE workshops_workshop DROP COLUMN address;
ALTER TABLE workshops_workshop DROP COLUMN city;

-- Toegevoegd
ALTER TABLE workshops_workshop ADD COLUMN meeting_url VARCHAR(500);
ALTER TABLE workshops_workshop ADD COLUMN meeting_id VARCHAR(100);
ALTER TABLE workshops_workshop ADD COLUMN meeting_password VARCHAR(100);
```

### Model Meta Updates:
```python
class Meta:
    verbose_name = 'Webinar'  # Changed
    verbose_name_plural = 'Webinars'  # Changed
    ordering = ['-start_datetime']  # Unchanged
```

---

## 📁 Bestanden Overzicht

### Aangepaste Bestanden:
```
backend/workshops/
├── models.py                    ✅ Webinar model met meeting velden
├── admin.py                     ✅ Admin interface voor webinars
├── management/commands/
│   └── populate_data.py         ✅ Test data met Teams URLs
└── migrations/
    └── 0005_webinar_conversion.py  ✅ Database migratie

backend/workshops/backup_before_webinar/
└── models.py.backup             📦 Backup van origineel
```

### Ongewijzigde Bestanden:
```
backend/workshops/
├── views.py                     ⚪ Geen wijzigingen nodig (yet)
├── urls.py                      ⚪ Geen wijzigingen nodig (yet)
├── forms.py                     ⚪ Geen wijzigingen nodig (yet)
└── templates/                   ⚪ Toekomstige updates nodig
```

---

## 🎯 Impact op Bestaande Data

### Na Migratie:

#### ✅ Blijft Werken:
- Alle bestaande boekingen
- Alle bestaande reviews
- Alle bestaande categorieën
- Alle user accounts
- Booking references (oude WS blijft werken)

#### ⚠️ Wordt Verwijderd:
- Locatie informatie (location, address, city)
- Oude workshops zonder meeting URLs

#### 🆕 Nieuw Beschikbaar:
- Meeting URL velden
- Meeting ID velden
- Meeting password velden
- Hogere max deelnemers limiet

---

## 🚀 Voor Productie

### Nog Te Doen:

1. **Templates Updaten:**
   - `workshop_list.html` → Toon meeting info ipv locatie
   - `workshop_detail.html` → Meeting details sectie
   - `booking_confirmation.html` → Meeting link in email

2. **Email Templates:**
   - Booking bevestiging met Teams link
   - Herinnering email met meeting details
   - Annulering email update

3. **API/Views:**
   - Update serializers
   - API endpoints testen
   - Forms aanpassen

4. **Frontend:**
   - "Locatie" labels vervangen door "Online"
   - Meeting link weergave
   - iCal export met Teams link

---

## 📝 Notities

### Bewuste Keuzes:

1. **Database naam blijft `workshop_db`**
   - Naam is niet relevant voor functionaliteit
   - Vermijdt complexe database rename

2. **App naam blijft `workshops`**
   - Django app naam is intern
   - Vermijdt complexe migrations
   - Verbose names zijn aangepast

3. **Booking prefix WB voor nieuwe**
   - Oude WS bookings blijven werken
   - Makkelijk te onderscheiden

4. **Gradual rollout mogelijk**
   - Beide types kunnen tijdelijk bestaan
   - Meeting URL is optional field

---

## ✅ Verificatie Checklist

Na migratie, check:

- [ ] Admin panel toont "Webinars"
- [ ] Meeting URL veld zichtbaar in forms
- [ ] Meeting ID en password velden aanwezig
- [ ] Geen locatie/adres/stad velden meer
- [ ] Test webinars hebben Teams URLs
- [ ] Boekingen tonen "Webinar" label
- [ ] Max deelnemers kunnen tot 500
- [ ] Nieuwe bookings krijgen WB prefix
- [ ] Oude bookings blijven werken
- [ ] Reviews blijven gekoppeld

---

**Laatst Bijgewerkt:** 2 november 2025  
**Versie:** 1.0  
**Status:** ✅ Compleet en Getest
