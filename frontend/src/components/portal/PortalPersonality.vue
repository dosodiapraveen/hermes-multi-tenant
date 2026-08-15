<template>
  <section class="personality-section">
    <div class="section-header">
      <h2>
        <BaseIcon name="brain" :size="24" />
        {{ agentName }} — Personality (SOUL.md)
      </h2>
    </div>

    <p class="intro-text">
      This file shapes <em>who I am and how I help you</em> — tone, style, and rules.
      Edit it below (or tell me <code>/personality</code> on Telegram) and I follow it in every reply.
    </p>

    <BaseCard class="editor-card">
      <textarea
        v-model="localPersonality"
        class="personality-editor"
        rows="16"
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

    <div class="tips">
      <h4>
        <BaseIcon name="lightbulb" :size="16" />
        Tips
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
import { BaseCard, BaseIcon, BaseButton } from '@design-system/components/ui'

export default {
  name: 'PortalPersonality',
  components: { BaseCard, BaseIcon, BaseButton },
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
.personality-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
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

.intro-text {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.intro-text code {
  padding: var(--spacing-1) var(--spacing-2);
  background: var(--color-gray-100);
  border-radius: var(--radius-md);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
}

.editor-card {
  padding: 0;
}

.personality-editor {
  width: 100%;
  min-height: 400px;
  padding: var(--spacing-4);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  line-height: var(--line-height-relaxed);
  color: var(--color-text-primary);
  background: var(--color-surface);
  border: none;
  border-bottom: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  resize: vertical;
  outline: none;
}

.personality-editor:focus {
  background: var(--color-gray-50);
}

.personality-editor::placeholder {
  color: var(--color-text-tertiary);
}

.editor-footer {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
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
</style>
