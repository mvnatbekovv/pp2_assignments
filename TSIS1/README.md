# TSIS1 PhoneBook

Extended PostgreSQL phonebook with:

- `contacts`, `phones`, and `groups` relational schema
- email, birthday, contact group, and date added
- multiple phone numbers per contact
- search by name, email, group, and all phones
- filter by group
- sort by name, birthday, or date added
- paginated console navigation with `next`, `prev`, `quit`
- JSON export and import with duplicate skip/overwrite choice
- extended CSV import
- PL/pgSQL procedure `add_phone`
- PL/pgSQL procedure `move_to_group`
- PL/pgSQL function `search_contacts`

## Setup

1. Create database in PostgreSQL:

```sql
CREATE DATABASE phonebook;
```

2. Edit `config.py` with your PostgreSQL username/password.

3. Install dependency:

```bash
pip install psycopg2-binary
```

4. Run SQL files:

```bash
psql -U postgres -d phonebook -f schema.sql
psql -U postgres -d phonebook -f procedures.sql
```

5. Start app:

```bash
python phonebook.py
```
