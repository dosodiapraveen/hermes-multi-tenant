#!/bin/bash
# Run database migrations

echo "Running database migrations..."

# Run migration 007
echo "Running 007_analytics_and_templates.sql..."
docker compose exec -T postgres psql -U hermes -d hermes < migrations/007_analytics_and_templates.sql

# Run migration 008
echo "Running 008_onboarding_and_examples.sql..."
docker compose exec -T postgres psql -U hermes -d hermes < migrations/008_onboarding_and_examples.sql

echo "Migrations complete!"
