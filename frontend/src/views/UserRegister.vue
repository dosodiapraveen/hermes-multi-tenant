<template>
  <div class="auth-page">
    <h1>Create your account</h1>
    <p>Link your email to your agent account.</p>
    <input v-model="email" placeholder="Email" type="email" />
    <input v-model="password" placeholder="Password (min 12 chars, uppercase, lowercase, number)" type="password" />
    <div v-if="!autoProfile">
      <input v-model="manual_profile_id" placeholder="Your agent ID" />
      <p class="hint">Your agent ID is shared by your admin. Or use the invite link they sent you.</p>
    </div>
    <button @click="register">Register</button>
    <p v-if="msg">{{ msg }}</p>
    <p v-if="verifyLink" class="verify-link">
      <a :href="verifyLink">Click here to verify your email</a>
    </p>
    <p>Already have an account? <a href="/user/login">Login</a></p>
  </div>
</template>
<script>
export default {
  data(){return{email:'',password:'',manual_profile_id:'',msg:'',verifyLink:'',autoProfile:false}},
  mounted(){
    const urlToken = new URLSearchParams(location.search).get('token')
    if(urlToken){ this.manual_profile_id = urlToken; this.autoProfile = true }
  },
  methods:{
    validateEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return re.test(email)
    },
    validatePassword(password) {
      if (password.length < 12) return 'Password must be at least 12 characters'
      if (!/[A-Z]/.test(password)) return 'Password must contain at least one uppercase letter'
      if (!/[a-z]/.test(password)) return 'Password must contain at least one lowercase letter'
      if (!/[0-9]/.test(password)) return 'Password must contain at least one number'
      return null
    },
    async register(){
      // Clear previous messages
      this.msg = ''
      this.verifyLink = ''

      // Validate profile ID
      const profile_id = this.manual_profile_id
      if(!profile_id){
        this.msg='❌ Missing agent profile ID. Use the invitation link from your admin.'
        return
      }

      // Validate email
      if (!this.email) {
        this.msg = '❌ Email is required'
        return
      }
      if (!this.validateEmail(this.email)) {
        this.msg = '❌ Please enter a valid email address'
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
        const r=await fetch('/api/auth/user/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:this.email,password:this.password,profile_id})})
        const d=await r.json()
        if(r.ok){
          this.msg='✅ Account created! ' + (d.message || 'Verification email sent.')
          if(d.verify_link) this.verifyLink = d.verify_link
        } else {
          this.msg='❌ '+(d.detail||'Registration failed')
        }
      }catch(e){this.msg='❌ Connection error'}
    }
  }
}
</script>
<style scoped>
.auth-page{max-width:400px;margin:40px auto;padding:20px;text-align:center}
input{width:100%;padding:10px;margin:8px 0;border:1px solid #ddd;border-radius:8px;font-size:16px;box-sizing:border-box}
button{width:100%;padding:12px;background:#6C5CE7;color:#fff;border:none;border-radius:8px;font-size:16px;cursor:pointer;margin:8px 0}
.hint{font-size:12px;color:#888;margin:-4px 0 8px}
.verify-link{margin-top:8px;padding:8px;background:#f0f0f0;border-radius:4px}
a{color:#6C5CE7}
</style>