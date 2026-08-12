<template>
  <div class="auth-page">
    <h1>Set New Password</h1>
    <input v-model="password" placeholder="New password (min 6 chars)" type="password" />
    <button @click="reset">Reset Password</button>
    <p v-if="msg">{{ msg }}</p>
    <p v-if="success"><a href="/user/login">Login now</a></p>
  </div>
</template>
<script>
export default {
  data(){return{password:'',msg:'',success:false}},
  methods:{
    async reset(){
      const token=new URLSearchParams(location.search).get('token')
      if(!token){this.msg='❌ Missing reset token';return}
      try{
        const r=await fetch('/api/auth/user/reset-password',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token,password:this.password})})
        const d=await r.json()
        if(r.ok){this.msg='✅ Password reset!';this.success=true}
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
a{color:#6C5CE7}
</style>