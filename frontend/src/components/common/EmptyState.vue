<template>
  <div class="empty-state">
    <div class="empty-icon">{{ icon }}</div>
    <h3 class="empty-title">{{ title }}</h3>
    <p class="empty-message">{{ message }}</p>
    <button v-if="actionText" @click="$emit('action')" class="empty-action">
      {{ actionText }}
    </button>
  </div>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    icon: {
      type: String,
      default: '📭'
    },
    title: {
      type: String,
      default: 'Nothing here yet'
    },
    message: {
      type: String,
      default: 'Get started by creating your first item.'
    },
    actionText: {
      type: String,
      default: ''
    }
  },
  emits: ['action']
}
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 48px 24px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.8;
}

.empty-title {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #2D3748;
}

.empty-message {
  margin: 0 0 24px 0;
  font-size: 14px;
  line-height: 1.6;
  color: #718096;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.empty-action {
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 500;
  color: white;
  background: #6C5CE7;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.empty-action:hover {
  background: #5B4BCF;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(108, 92, 231, 0.2);
}

@media (max-width: 640px) {
  .empty-state {
    padding: 32px 20px;
  }

  .empty-icon {
    font-size: 48px;
  }

  .empty-title {
    font-size: 18px;
  }
}
</style>
