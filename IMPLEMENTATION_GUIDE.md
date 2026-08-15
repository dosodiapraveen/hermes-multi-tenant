# Implementation Guide: User Adoption Improvements

## Overview

This guide covers the implementation of comprehensive user adoption improvements including:
- Analytics tracking and insights
- Templates system (projects, workflows, conversations)
- Onboarding & tutorial system
- Improved dashboard UX

## Implementation Status

### ✅ Phase 1: Backend Infrastructure (COMPLETE)

**Database Schema:**
- ✅ `007_analytics_and_templates.sql` - Analytics & templates tables
- ✅ `008_onboarding_and_examples.sql` - Onboarding tables

**Backend Services:**
- ✅ Analytics service with event tracking
- ✅ Templates API (projects, workflows, conversations)
- ✅ Onboarding API (wizard, checklist, tutorials)
- ✅ Template seeder service

**API Endpoints:**
- ✅ `/api/me/analytics/*` - Analytics and goals
- ✅ `/api/templates/*` - Template browsing and usage
- ✅ `/api/me/onboarding/*` - Onboarding progress

### ✅ Phase 2: Frontend Shared Components (COMPLETE)

**Components Created:**
- ✅ LoadingSpinner.vue - Reusable loading states
- ✅ ErrorMessage.vue - Error display with retry
- ✅ ConfirmDialog.vue - Modal confirmations
- ✅ SuccessToast.vue - Toast notifications
- ✅ EmptyState.vue - Empty state displays
- ✅ apiClient.js - Centralized API client

### 🔄 Phase 3: Dashboard UX Improvements (IN PROGRESS)

**Remaining Work:**
- ⏳ Refactor UserPortal.vue with:
  - Parallel API loading (Promise.all)
  - Per-endpoint error handling
  - Loading states with spinners
  - ConfirmDialog for deletions
- ⏳ Extract portal components:
  - PortalHeader.vue
  - DashboardTab.vue
  - NotesTab.vue
  - IdeasTab.vue
  - ProjectsTab.vue
- ⏳ Add accessibility (ARIA, keyboard nav)

### ⏳ Phase 4: Onboarding System (PENDING)

**Components to Create:**
- OnboardingWizard.vue - 6-step first-time experience
- OnboardingChecklist.vue - Progress checklist widget
- TutorialOverlay.vue - Interactive tutorials
- HelpCenter.vue - FAQ and help content

### ⏳ Phase 5: Analytics Dashboard (PENDING)

**Components to Create:**
- AnalyticsDashboard.vue - Usage metrics
- MetricsCard.vue - Stat display cards
- FeatureAdoptionChart.vue - Usage visualization
- ActivityTimeline.vue - Activity history

### ⏳ Phase 6: Templates System (PENDING)

**Components to Create:**
- TemplateSelector.vue - Template browser
- TemplateCard.vue - Template preview
- TemplatePreview.vue - Detailed view

### ⏳ Phase 7-8: Testing & Deployment (PENDING)

---

## Testing the Backend Changes

### Step 1: Run Database Migrations

```bash
# Option A: Use the migration script
./run_migrations.sh

# Option B: Manual migration
docker compose exec -T postgres psql -U hermes -d hermes < migrations/007_analytics_and_templates.sql
docker compose exec -T postgres psql -U hermes -d hermes < migrations/008_onboarding_and_examples.sql
```

### Step 2: Verify Tables Created

```bash
docker compose exec postgres psql -U hermes -d hermes -c "\dt user_analytics; \dt project_templates; \dt onboarding_progress;"
```

Expected output should show the new tables.

### Step 3: Seed Templates

```bash
# Option A: Use the seeder script
./seed_templates.sh

# Option B: Manual seeding
docker compose exec api python -m app.services.template_seeder
```

This will populate:
- 8 project templates
- 5 workflow templates
- 6 conversation examples

### Step 4: Restart API

```bash
docker compose restart api
```

### Step 5: Test API Endpoints

```bash
# Get your portal token from browser cookies or localStorage
export TOKEN="your_portal_token_here"

# Test analytics summary
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/me/analytics/summary

# Test project templates
curl http://localhost:8000/api/templates/projects

# Test onboarding status
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/me/onboarding
```

---

## Frontend Integration (Next Steps)

### Phase 3: Refactor UserPortal.vue

**Key Changes Needed:**

1. **Import Shared Components:**
```vue
<script>
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ErrorMessage from '@/components/common/ErrorMessage.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import SuccessToast from '@/components/common/SuccessToast.vue'
import apiClient from '@/utils/apiClient'
</script>
```

2. **Replace Sequential API Calls with Parallel:**
```javascript
// OLD: Sequential fetching
async fetchData() {
  await this.fetchNotes()
  await this.fetchIdeas()
  await this.fetchProjects()
  // ... etc
}

// NEW: Parallel fetching
async fetchData() {
  this.loading = true
  try {
    const [notesData, ideasData, projectsData] = await Promise.all([
      apiClient.get('/api/me/notes'),
      apiClient.get('/api/me/ideas'),
      apiClient.get('/api/me/projects')
    ])

    this.notes = notesData.notes
    this.ideas = ideasData.ideas
    this.projects = projectsData.projects
  } catch (error) {
    this.error = error.message
  } finally {
    this.loading = false
  }
}
```

3. **Replace confirm() with ConfirmDialog:**
```vue
<!-- OLD -->
<button @click="confirm('Delete?') && deleteNote(id)">Delete</button>

<!-- NEW -->
<ConfirmDialog
  :isOpen="confirmDialog.isOpen"
  :title="confirmDialog.title"
  :message="confirmDialog.message"
  type="danger"
  @confirm="handleConfirmAction"
  @cancel="confirmDialog.isOpen = false"
/>
```

4. **Add Loading States:**
```vue
<template>
  <div v-if="loading" class="loading-container">
    <LoadingSpinner size="lg" />
    <p>Loading your data...</p>
  </div>

  <ErrorMessage
    v-if="error"
    :message="error"
    severity="error"
    :retryable="true"
    @retry="fetchData"
  />

  <div v-else>
    <!-- Content -->
  </div>
</template>
```

### Phase 4: Create Onboarding Components

Location: `/frontend/src/components/onboarding/`

1. **OnboardingWizard.vue** - Show on first login
2. **OnboardingChecklist.vue** - Persistent progress widget
3. **TutorialOverlay.vue** - Feature tutorials

### Phase 5: Create Analytics Dashboard

Location: `/frontend/src/components/analytics/`

1. **AnalyticsDashboard.vue** - Main analytics view
2. Fetch data from `/api/me/analytics/summary`
3. Display charts and insights

### Phase 6: Create Templates Integration

Location: `/frontend/src/components/templates/`

1. **TemplateSelector.vue** - Template browser modal
2. Integrate with Projects tab "Use Template" button
3. Call `/api/templates/projects/{id}/apply`

---

## Database Schema Reference

### Analytics Tables

**user_analytics**: Aggregated metrics (daily/weekly/monthly)
- `messages_sent`, `notes_created`, `search_queries`, etc.
- `period_type` ('daily', 'weekly', 'monthly')

**analytics_events**: Fine-grained event log
- `event_type` (note_created, search_query, etc.)
- `event_category` (message, content, search, etc.)

**user_goals**: Goal tracking
- `goal_type` (weekly_notes, monthly_searches, etc.)
- `target_value`, `current_value`
- Auto-complete when target reached

### Templates Tables

**project_templates**: Project blueprints
- `default_tasks[]`, `default_research_topics[]`
- `category`, `industry`, `is_featured`

**workflow_templates**: Repeatable workflows
- `steps[]` (JSONB with step details)
- `prompts[]`, `expected_duration_minutes`

**conversation_examples**: Starter conversations
- `starter_prompt`, `example_response`
- `follow_up_prompts[]`

### Onboarding Tables

**onboarding_progress**: User onboarding state
- `wizard_completed`, `checklist_items` (JSONB)
- `first_note_at`, `first_project_at` (milestones)

---

## API Endpoint Reference

### Analytics Endpoints

```
GET  /api/me/analytics/summary           # Overall stats
GET  /api/me/analytics/daily?days=30     # Daily breakdown
GET  /api/me/analytics/weekly?weeks=12   # Weekly breakdown
GET  /api/me/analytics/feature-adoption  # Usage by feature
GET  /api/me/analytics/goals             # Active goals
POST /api/me/analytics/goals             # Create goal
PUT  /api/me/analytics/goals/{id}        # Update progress
POST /api/me/analytics/track             # Track event
```

### Templates Endpoints

```
GET  /api/templates/projects                  # List project templates
GET  /api/templates/workflows                 # List workflows
GET  /api/templates/conversations             # List examples
POST /api/templates/projects/{id}/apply       # Create from template
POST /api/templates/workflows/{id}/track      # Track workflow usage
POST /api/templates/conversations/{id}/track  # Track example usage
GET  /api/me/templates/usage                  # User's template history
```

### Onboarding Endpoints

```
GET  /api/me/onboarding                     # Get progress
POST /api/me/onboarding/wizard/complete     # Complete wizard
POST /api/me/onboarding/checklist/{item}    # Update checklist item
POST /api/me/onboarding/checklist/dismiss   # Dismiss checklist
GET  /api/me/onboarding/tutorials/{id}      # Get tutorial progress
POST /api/me/onboarding/tutorials/{id}/step # Update tutorial step
```

---

## Deployment Checklist

### Backend
- [x] Migrations created (007, 008)
- [x] Services implemented
- [x] Routers registered
- [x] Template seeder ready
- [ ] Run migrations on production DB
- [ ] Seed templates
- [ ] Restart API service
- [ ] Test endpoints with curl

### Frontend
- [x] Shared components created
- [x] API client created
- [ ] Refactor UserPortal.vue
- [ ] Create onboarding components
- [ ] Create analytics components
- [ ] Create template components
- [ ] Build frontend
- [ ] Deploy to production

### Testing
- [ ] Test analytics tracking
- [ ] Test template application
- [ ] Test onboarding flow (new user)
- [ ] Test goal tracking
- [ ] Verify accessibility (WCAG AA)
- [ ] Test mobile responsive design

---

## Rollback Plan

If issues arise:

```bash
# Rollback migrations
docker compose exec postgres psql -U hermes -d hermes -c "
  DROP TABLE IF EXISTS analytics_events CASCADE;
  DROP TABLE IF EXISTS user_analytics CASCADE;
  DROP TABLE IF EXISTS conversation_insights CASCADE;
  DROP TABLE IF EXISTS user_goals CASCADE;
  DROP TABLE IF EXISTS project_templates CASCADE;
  DROP TABLE IF EXISTS workflow_templates CASCADE;
  DROP TABLE IF EXISTS conversation_examples CASCADE;
  DROP TABLE IF EXISTS template_usage CASCADE;
  DROP TABLE IF EXISTS onboarding_progress CASCADE;
  DROP TABLE IF EXISTS tutorial_progress CASCADE;
  DROP TABLE IF EXISTS help_center_activity CASCADE;
  DELETE FROM schema_migrations WHERE version IN ('007_analytics_and_templates', '008_onboarding_and_examples');
"

# Restart services
docker compose restart api
```

---

## Performance Considerations

### Database Indexes
All critical columns have indexes:
- `analytics_events`: user_id, event_type, created_at
- `user_goals`: user_id, is_active
- Templates: category, is_active, is_featured

### API Caching
Frontend `apiClient.js` includes:
- 5-minute cache for GET requests
- Request deduplication
- Automatic retry with exponential backoff

### Analytics Tracking
- Async event tracking (non-blocking)
- Failed tracking doesn't break user experience
- Events stored indefinitely, aggregates computed on-demand

---

## Security Notes

### Authentication
- All endpoints use existing `resolve_user()` dependency
- Session token validation with expiration
- CSRF protection on all state-changing operations

### Data Privacy
- Analytics events tied to user_id
- No PII stored in event_data
- Users can only access their own data

### Input Validation
- Template application validates ownership
- Goal updates validate user owns goal
- Onboarding updates validate user session

---

## Support & Troubleshooting

### Common Issues

**Issue: Migrations fail with "relation already exists"**
Solution: Tables use `IF NOT EXISTS`, safe to re-run

**Issue: Template seeding fails**
Solution: Tables may already have data, seeder uses `ON CONFLICT DO NOTHING`

**Issue: API returns 401 on analytics endpoints**
Solution: Ensure portal_token cookie is set or Authorization header present

**Issue: Frontend can't import shared components**
Solution: Use `@/components/common/ComponentName.vue` with @ alias

---

## Next Actions

1. **Test Backend (Now):**
   ```bash
   ./run_migrations.sh
   ./seed_templates.sh
   docker compose restart api
   ```

2. **Verify (Now):**
   ```bash
   # Check tables exist
   docker compose exec postgres psql -U hermes -d hermes -c "\dt"

   # Test API endpoints
   curl http://localhost:8000/api/templates/projects
   ```

3. **Continue Frontend (Next):**
   - Refactor UserPortal.vue with shared components
   - Create onboarding wizard
   - Create analytics dashboard
   - Create template selector

4. **Final Testing:**
   - Manual testing of all flows
   - Accessibility audit
   - Mobile responsive check

5. **Deploy:**
   - Run migrations on production
   - Seed production templates
   - Deploy frontend build
   - Monitor logs for errors

---

## Contact

For questions or issues, refer to the implementation plan document or check the codebase comments.
