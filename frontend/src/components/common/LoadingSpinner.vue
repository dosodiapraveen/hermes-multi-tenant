<template>
  <div :class="['spinner', `spinner-${size}`]" :aria-label="label">
    <div class="spinner-circle"></div>
  </div>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  props: {
    size: {
      type: String,
      default: 'md',
      validator: value => ['sm', 'md', 'lg'].includes(value)
    },
    label: {
      type: String,
      default: 'Loading...'
    }
  }
}
</script>

<style scoped>
.spinner {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.spinner-sm { width: 16px; height: 16px; }
.spinner-md { width: 24px; height: 24px; }
.spinner-lg { width: 40px; height: 40px; }

.spinner-circle {
  width: 100%;
  height: 100%;
  border: 2px solid rgba(108, 92, 231, 0.2);
  border-top-color: #6C5CE7;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.spinner-sm .spinner-circle { border-width: 1.5px; }
.spinner-lg .spinner-circle { border-width: 3px; }

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
