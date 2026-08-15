<template>
  <div style="min-height:100vh;background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;font-family:sans-serif">
    <div style="background:#fff;border-radius:16px;padding:40px;max-width:420px;width:90%;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,.3)">
      <div style="font-size:44px;margin-bottom:12px">{{ icon }}</div>
      <h1 style="font-size:22px;color:#1A1A2E;margin:0 0 8px">{{ msg }}</h1>
      <p style="color:#636E70;font-size:14px;line-height:1.6;margin:0 0 20px">{{ sub }}</p>
      <a v-if="success" href="/user/login" style="display:inline-block;background:#6C5CE7;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none">Login now</a>
    </div>
  </div>
</template>
<script>
export default {
  data(){return{icon:'⏳',msg:'Verifying...',sub:'Please wait while we confirm your email.',success:false}},
  async mounted(){
    const token=new URLSearchParams(location.search).get('token')
    if(!token){this.icon='❌';this.msg='Missing verification token';this.sub='The link is invalid. Please request a new one.';return}
    try{
      const r=await fetch('/api/auth/user/verify?token='+token)
      const d=await r.json().catch(()=>({}))
      if(r.ok){this.icon='✅';this.msg='Email verified!';this.sub=d.message||'Your request is now with an admin for review.';this.success=true}
      else {this.icon='❌';this.msg='Verification failed';this.sub=d.detail||'Invalid or expired link'}
    }catch(e){this.icon='❌';this.msg='Connection error';this.sub='Please try again.'}
  }
}
</script>
