<template>
  <div class="auth-page">
    <h1>Set New Password</h1>
    <input v-model="password" placeholder="New password (min 12 chars, uppercase, lowercase, number)" type="password" />
    <button @click="reset">Reset Password</button>
    <p v-if="msg">{{ msg }}</p>
    <p v-if="success"><a href="/user/login">Login now</a></p>
  </div>
</template>
<script>
export default {
  data(){return{password:'',msg:'',success:false}},
  methods:{
    validatePassword(password) {
      if (password.length < 12) return 'Password must be at least 12 characters'
      if (!/[A-Z]/.test(password)) return 'Password must contain at least one uppercase letter'
      if (!/[a-z]/.test(password)) return 'Password must contain at least one lowercase letter'
      if (!/[0-9]/.test(password)) return 'Password must contain at least one number'
      return null
    },
    async reset(){
      // Clear previous messages
      this.msg = ''
      this.success = false

      const token=new URLSearchParams(location.search).get('token')
      if(!token){
        this.msg='❌ Missing reset token'
        return
      }

      // Validate password
      if (!this.password) {
        this.msg = '❌ Password is required'
        return
      }
      const passwordError = this.validatePassword(this.password)
      if (passwordError) {
        this.msg = '❌ ' + passwordError
        return
      }

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