# Synthetic dataset provenance

The five records in `shipsafe/seed.py` were authored specifically for this
ShipSafe scaffold. All labels and addresses are invented; no external dataset,
customer data, scraped content, or personal information was used. There are no
third-party dataset licensing dependencies.

Fixed IDs 1–5 cover pending, shipped, and delivered orders, a missing address
(NULL), an empty address, an apostrophe, Unicode text, and a multiline address.
Missing/empty addresses are valid in this tiny app. Customer labels must be
nonempty, and statuses come from the three-value app contract.

The immutable Python tuple is the fixture. Each rehearsal builds a new v1
SQLite database in a unique temporary directory and inserts these records.
There is no checked-in binary database and no CLI option for a user's database.
The database is deleted after the run, including failed runs. Timings vary;
seed records, operation order, and verdict for unchanged inputs are repeatable.
