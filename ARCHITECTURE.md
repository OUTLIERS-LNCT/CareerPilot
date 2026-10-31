# Package layout note

The initial working scaffold centralizes models, schemas, dependencies, service logic, and FastAPI route registrations in `app/main.py` so a beginner can follow a single request end to end. Import facades under `app/models`, `app/schemas`, `app/services`, and `app/api` provide stable module names for gradual extraction. Keep route handlers thin as the application grows and move each domain to its own file before adding many features.
