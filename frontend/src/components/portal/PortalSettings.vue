<template>
  <section class="settings-section">
    <div class="section-header">
      <h2>
        <BaseIcon name="settings" :size="24" />
        Settings
      </h2>
    </div>

    <!-- Appearance -->
    <BaseCard class="settings-card">
      <h3 class="settings-group-title">
        <BaseIcon name="sun" :size="18" />
        Appearance
      </h3>
      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-label">Theme</span>
          <span class="setting-description">Choose light or dark mode</span>
        </div>
        <BaseThemeToggle />
      </div>
    </BaseCard>

    <!-- Agent Personality -->
    <BaseCard class="settings-card">
      <h3 class="settings-group-title">
        <BaseIcon name="brain" :size="18" />
        {{ agentName }} — Personality (SOUL.md)
      </h3>
      <p class="settings-description">
        This file shapes <em>who I am and how I help you</em> — tone, style, and rules.
        Edit it below (or tell me <code>/personality</code> on Telegram) and I follow it in every reply.
      </p>

      <textarea
        v-model="localPersonality"
        class="personality-editor"
        rows="14"
        placeholder="# Agent Personality

## Voice & Tone
- Be friendly and professional
- Use clear, concise language
- Show enthusiasm when appropriate

## Behavior Rules
- Always prioritize user privacy
- Ask clarifying questions when unsure
- Provide context for recommendations

## Special Instructions
- Remember user preferences
- Follow up on previous conversations
- Suggest proactive improvements"
      ></textarea>

      <div class="editor-footer">
        <BaseButton
          :loading="saving"
          :disabled="!hasChanges"
          @click="save"
        >
          {{ saving ? 'Saving...' : 'Save Personality' }}
        </BaseButton>
        <Transition name="fade">
          <span v-if="saved" class="saved-indicator">
            <BaseIcon name="check" :size="16" />
            Saved
          </span>
        </Transition>
      </div>
    </BaseCard>

    <!-- Tips -->
    <div class="tips">
      <h4>
        <BaseIcon name="lightbulb" :size="16" />
        Personality Tips
      </h4>
      <ul>
        <li>Use markdown formatting for structure</li>
        <li>Define specific behaviors you want</li>
        <li>Include examples of preferred responses</li>
        <li>Set boundaries for what topics to avoid</li>
      </ul>
    </div>
  </section>
</template>

<script>
import { BaseCard, BaseIcon, BaseButton, BaseThemeToggle } from '@design-system/components/ui'

export default {
  name: 'PortalSettings',
  components: { BaseCard, BaseIcon, BaseButton, BaseThemeToggle },
  props: {
    personality: { type: String, default: '' },
    agentName: { type: String, default: 'Agent' }
  },
  emits: ['save'],
  data() {
    return {
      localPersonality: this.personality,
      saving: false,
      saved: false,
      originalPersonality: this.personality
    }
  },
  computed: {
    hasChanges() {
      return this.localPersonality !== this.originalPersonality
    }
  },
  watch: {
    personality: {
      handler(val) {
        this.localPersonality = val
        this.originalPersonality = val
      },
      immediate: true
    }
  },
  methods: {
    async save() {
      this.saving = true
      this.saved = false

      try {
        const token = localStorage.getItem('portal_token')
        const response = await fetch('/api/me/personality', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ personality: this.localPersonality })
        })

        if (response.ok) {
          this.originalPersonality = this.localPersonality
          this.saved = true
          this.$emit('save', this.localPersonality)

          setTimeout(() => {
            this.saved = false
          }, 3000)
        } else {
          const data = await response.json()
          alert('Failed to save: ' + (data.error || 'Unknown error'))
        }
      } catch (e) {
        alert('Failed to save: ' + e.message)
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
.settings-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-5);
}

.section-header h2 {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.settings-card {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.settings-group-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin: 0;
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.settings-description {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.settings-description code {
  padding: var(--spacing-1) var(--spacing-2);
  background: var(--color-gray-100);
  border-radius: var(--radius-md);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-4);
  padding: var(--spacing-3) 0;
  border-top: 1px solid var(--color-border-light);
}

.setting-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.setting-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.setting-description {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.personality-editor {
  width: 100%;
  min-height: 320px;
  padding: var(--spacing-4);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  line-height: var(--line-height-relaxed);
  color: var(--color-text-primary);
  background: var(--color-gray-50);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  resize: vertical;
  outline: none;
  transition: border-color var(--transition-fast), background var(--transition-fast);
}

.personality-editor:focus {
  border-color: var(--color-primary-500);
  background: var(--color-surface);
}

.personality-editor::placeholder {
  color: var(--color-text-tertiary);
}

.editor-footer {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.saved-indicator {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-success-600);
}

.tips {
  padding: var(--spacing-4);
  background: var(--color-primary-50);
  border-radius: var(--radius-lg);
}

.tips h4 {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin: 0 0 var(--spacing-2);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-primary-700);
}

.tips ul {
  margin: 0;
  padding-left: var(--spacing-5);
}

.tips li {
  font-size: var(--font-size-sm);
  color: var(--color-primary-600);
  line-height: var(--line-height-relaxed);
}

/* Fade animation */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Mobile */
@media (max-width: 640px) {
  .setting-row {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-3);
  }
}
</style>
