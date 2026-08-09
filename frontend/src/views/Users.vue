<template>
  <div>
    <h2>Users</h2>
    <p class="sub">Manage user profiles</p>
    <table><thead><tr><th>Phone</th><th>Agent</th><th>Plan</th><th>Status</th><th>Model</th></tr></thead>
      <tbody><tr v-for="u in users" :key="u.id">
        <td>{{ u.phone_number || '—' }}</td><td>{{ u.agent_name }}</td>
        <td><span class="badge">{{ u.plan }}</span></td>
        <td><span :class="u.is_active ? 'green' : 'muted'">{{ u.is_active ? 'Active' : 'Inactive' }}</span></td>
        <td>{{ u.primary_model }}</td>
      </tr></tbody>
    </table>
  </div>
</template>

<script>
export default {
  data() { return { users:[] }},
  async mounted() {
    const r = await fetch('/api/admin/users', { headers:{'Authorization':'Bearer '+localStorage.getItem('token')} })
    this.users = await r.json()
  }
}
</script>
