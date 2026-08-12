<template>
  <div class="auth-page">
    <h1>Login</h1>
    <input v-model="email" placeholder="Email" type="email" />
    <input v-model="password" placeholder="Password" type="password" />
    <button @click="login">Login</button>
    <p v-if="msg">{{ msg }}</p>
    <p><a href="/user/forgot">Forgot password?</a></p>
    <p>No account? <a href="/user/register">Register</a></p>
  </div>
</template>
<script>
export default {
  data(){return{email:'',password:'',msg:''}},
  methods:{
    async login(){
      try{
        const r=await fetch('/api/auth/user/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:this.email,password:this.password})})
        const d=await r.json()
        if(r.ok){localStorage.setItem('portal_token',d.token);localStorage.setItem('profile_id',d.profile_id);window.location='/portal'}
        else this.msg='❌ '+(d.detail||'Login failed')
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