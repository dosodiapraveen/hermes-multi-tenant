<template>
  <div class="auth-page">
    <h1>Forgot Password</h1>
    <input v-model="email" placeholder="Email" type="email" />
    <button @click="forgot">Send Reset Link</button>
    <p v-if="msg">{{ msg }}</p>
    <p><a href="/user/login">Back to login</a></p>
  </div>
</template>
<script>
export default {
  data(){return{email:'',msg:''}},
  methods:{
    async forgot(){
      try{
        const r=await fetch('/api/auth/user/forgot-password',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:this.email})})
        const d=await r.json()
        this.msg='✅ If that email exists, a reset link has been sent.'
      }catch(e){this.msg='❌ Connection error'}
    }
  }
}
</script>
<style scoped>
.auth-page{max-width:400px;margin:40px auto;padding:20px;text-align:center}
input{width:100%;padding:10px;margin:8px 0;border:1px solid #ddd;border-radius:8px;font-size:16px}
button{width:100%;padding:12px;background:#6C5CE7;color:#fff;border:none;border-radius:8px;font-size:16px;cursor:pointer;margin:8px 0}
a{color:#6C5CE7}
</style>