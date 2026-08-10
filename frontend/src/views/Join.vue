<template>
  <div class="join-page">
    <div class="card">
      <div class="logo">H</div>
      <h1>You're Invited!</h1>
      <div class="check">✓</div>
      <h2>Your Agent is Ready</h2>
      <div class="steps">
        <div class="step"><span class="num">1</span> Tap the button below</div>
        <div class="step"><span class="num">2</span> Send "<strong>/start {{ code }}</strong>" to the bot</div>
        <div class="step"><span class="num">3</span> You're all set!</div>
      </div>
      <a :href="'https://t.me/BotBePreparedBot?start=' + code" class="btn" target="_blank">
        Open Telegram
      </a>
      <p class="tip">Don't have Telegram? <a href="https://telegram.org">Download it first</a></p>
    </div>
  </div>
</template>
<script>
export default {
  data() { return { code: '' }},
  mounted() { this.code = this.$route.params.code || '' }
}
</script>
<style scoped>
.join-page { display:flex; align-items:center; justify-content:center; min-height:100vh; background:#F0F2F5; }
.card { background:white; border-radius:16px; padding:40px; text-align:center; max-width:420px; width:90%; box-shadow:0 8px 30px rgba(0,0,0,0.06); }
.logo { width:48px; height:48px; background:linear-gradient(135deg,#6C5CE7,#A29BFE); border-radius:12px; display:inline-flex; align-items:center; justify-content:center; font-size:24px; font-weight:800; color:#fff; margin-bottom:16px; }
h1 { font-size:24px; font-weight:700; color:#1A1A2E; margin-bottom:8px; }
h2 { font-size:18px; font-weight:600; color:#1A1A2E; margin:8px 0; }
.check { width:40px; height:40px; background:#00C875; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; color:#fff; font-size:20px; margin-bottom:8px; margin-left:auto; margin-right:auto; }
.steps { text-align:left; margin:20px 0; }
.step { padding:10px 0; font-size:14px; color:#333; border-bottom:1px solid #F0F2F5; }
.num { display:inline-flex; width:24px; height:24px; background:#6C5CE7; color:#fff; border-radius:50%; align-items:center; justify-content:center; font-size:12px; font-weight:700; margin-right:10px; }
.btn { display:inline-block; margin-top:16px; padding:14px 32px; background:#6C5CE7; color:#fff; border-radius:10px; font-weight:600; text-decoration:none; transition:background 0.2s; }
.btn:hover { background:#5A4BD1; }
.tip { margin-top:16px; font-size:12px; color:#636E70; }
.tip a { color:#6C5CE7; text-decoration:none; }
</style>