<template>
  <div class="auth-page">
    <h1>{{ msg }}</h1>
    <p v-if="success"><a href="/portal-login">Login now</a></p>
  </div>
</template>
<script>
export default {
  data(){return{msg:'Verifying...',success:false}},
  async mounted(){
    const token=new URLSearchParams(location.search).get('token')
    if(!token){this.msg='❌ Missing verification token';return}
    try{
      const r=await fetch('/api/auth/user/verify?token='+token)
      if(r.ok){this.msg='✅ Email verified!';this.success=true}
      else this.msg='❌ Invalid or expired link'
    }catch(e){this.msg='❌ Connection error'}
  }
}
</script>
<style scoped>
.auth-page{max-width:400px;margin:40px auto;padding:20px;text-align:center}
a{color:#6C5CE7}
</style>