<template>
  <div class="auth-page">
    <h1>Create your account</h1>
    <p>Link your email to your agent profile.</p>
    <input v-model="email" placeholder="Email" type="email" />
    <input v-model="password" placeholder="Password (min 6 chars)" type="password" />
    <input v-model="profile_id" placeholder="Your agent ID" />
    <p class="hint">Your agent ID is shared by your admin.</p>
    <button @click="register">Register</button>
    <p v-if="msg">{{ msg }}</p>
    <p>Already have an account? <a href="/portal-login">Login</a></p>
  </div>
</template>
<script>
export default {
  data(){return{email:'',password:'',profile_id:'',msg:''}},
  methods:{
    async register(){
      try{
        const r=await fetch('/api/auth/user/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:this.email,password:this.password,profile_id:this.profile_id})})
        const d=await r.json()
        if(r.ok) this.msg='✅ Verification email sent! Check your inbox.'
        else this.msg='❌ '+d.detail
      }catch(e){this.msg='❌ Connection error'}
    }
  }
}
</script>
<style scoped>
.auth-page{max-width:400px;margin:40px auto;padding:20px;text-align:center}
input{width:100%;padding:10px;margin:8px 0;border:1px solid #ddd;border-radius:8px;font-size:16px}
button{width:100%;padding:12px;background:#6C5CE7;color:#fff;border:none;border-radius:8px;font-size:16px;cursor:pointer;margin:8px 0}
.hint{font-size:12px;color:#888;margin:-4px 0 8px}
a{color:#6C5CE7}
</style>