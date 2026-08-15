#!/bin/bash
# Seed templates into the database

echo "Seeding templates..."

docker compose exec api python -c "
import asyncio
import sys
sys.path.insert(0, '/app')
from app.services.template_seeder import seed_all_templates

asyncio.run(seed_all_templates())
"

echo "Template seeding complete!"
