<template>
  <div class="landing">
    <header class="header">
      <div class="logo"><div class="logo-icon">H</div><span class="logo-text">Hermes</span></div>
      <nav class="header-nav">
        <a href="#features">Features</a>
        <a href="#pricing">Pricing</a>
        <router-link to="/login" class="btn-outline">Admin Login</router-link>
      </nav>
    </header>

    <section class="hero">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <div class="badge">v0.1 — Now in Beta</div>
        <h1>AI Agents for<br/><span class="gradient">Every User.</span></h1>
        <p>Deploy personalized AI agents for your customers in minutes. Each user gets their own isolated agent with Telegram, web access, and a private knowledge vault.</p>
        <div class="hero-actions">
          <router-link to="/login" class="btn-primary">Get Started</router-link>
          <a href="#features" class="btn-ghost">Learn More</a>
        </div>
      </div>
    </section>

    <section id="features" class="features">
      <h2>Everything you need to deploy AI agents<br/>for your users at scale</h2>
      <div class="feature-grid">
        <div class="feature-card"><div class="icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg></div><h3>Multi-Tenant Platform</h3><p>Each user gets a completely isolated agent with their own config, memory, skills, and data. No cross-contamination.</p></div>
        <div class="feature-card"><div class="icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div><h3>Telegram Integration</h3><p>Users message their agent on Telegram. Real-time AI responses with automatic failover between models.</p></div>
        <div class="feature-card"><div class="icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></div><h3>Obsidian Vaults</h3><p>Every user gets a private knowledge vault. Agents can read, write, and search notes — a persistent second brain.</p></div>
        <div class="feature-card"><div class="icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg></div><h3>Model Flexibility</h3><p>Swap between Claude, GPT, DeepSeek, and more per user. Primary + backup auto-failover ensures uptime.</p></div>
        <div class="feature-card"><div class="icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg></div><h3>Admin Dashboard</h3><p>Full control panel to manage users, generate invite links, configure models, and monitor usage in real-time.</p></div>
        <div class="feature-card"><div class="icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div><h3>Enterprise Security</h3><p>PostgreSQL with Row-Level Security, encrypted API keys, isolated filesystems per user, and HTTPS everywhere.</p></div>
      </div>
    </section>

    <section id="pricing" class="pricing">
      <h2>Simple pricing.<br/><span class="gradient">Scale as you grow.</span></h2>
      <div class="pricing-grid">
        <div class="plan"><h3>Basic</h3><div class="price">$5<span>/mo</span></div><ul><li>1 agent</li><li>100 msgs/day</li><li>Single AI model</li><li>Obsidian vault</li></ul><router-link to="/login" class="btn-primary">Get Started</router-link></div>
        <div class="plan popular"><div class="pop-badge">Most Popular</div><h3>Pro</h3><div class="price">$15<span>/mo</span></div><ul><li>Up to 3 agents</li><li>500 msgs/day</li><li>Multi-model support</li><li>Obsidian vault</li><li>Web browser access</li></ul><router-link to="/login" class="btn-primary">Get Started</router-link></div>
        <div class="plan"><h3>Business</h3><div class="price">$35<span>/mo</span></div><ul><li>Up to 10 agents</li><li>2000 msgs/day</li><li>All models + vision</li><li>Priority support</li><li>Custom integrations</li></ul><router-link to="/login" class="btn-primary">Get Started</router-link></div>
      </div>
    </section>

    <footer class="footer">
      <div class="footer-inner">
        <div class="footer-brand"><div class="logo-icon">H</div><span>Hermes</span></div>
        <div class="footer-links"><a href="#features">Features</a><a href="#pricing">Pricing</a><router-link to="/login">Admin Login</router-link></div>
        <div class="footer-copy">Built with Hermes Agent by Nous Research</div>
      </div>
    </footer>
  </div>
</template>

<script>
export default { name: 'LandingView' }
</script>

<style scoped>
* { scroll-behavior: smooth; }
.landing { font-family:'Inter',-apple-system,sans-serif; color:#1A1A2E; overflow-x:hidden; }
.header { display:flex; align-items:center; justify-content:space-between; padding:16px 40px; position:fixed; top:0; left:0; right:0; z-index:100; background:rgba(255,255,255,0.85); backdrop-filter:blur(12px); border-bottom:1px solid rgba(0,0,0,0.04); }
.logo { display:flex; align-items:center; gap:10px; }
.logo-icon { width:32px; height:32px; background:linear-gradient(135deg,#6C5CE7,#A29BFE); border-radius:8px; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:16px; color:#fff; }
.logo-text { font-size:18px; font-weight:700; letter-spacing:-0.3px; }
.header-nav { display:flex; align-items:center; gap:24px; }
.header-nav a { color:#636E70; text-decoration:none; font-size:14px; font-weight:500; }
.header-nav a:hover { color:#1A1A2E; }
.btn-outline { padding:8px 20px; border:1.5px solid #6C5CE7; border-radius:8px; color:#6C5CE7; font-weight:600; font-size:13px; }
.btn-outline:hover { background:#6C5CE7; color:#fff; }
.hero { position:relative; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:120px 40px 80px; overflow:hidden; }
.hero-bg { position:absolute; inset:0; background:radial-gradient(ellipse at 20% 50%,rgba(108,92,231,0.08) 0%,transparent 50%),radial-gradient(ellipse at 80% 20%,rgba(0,206,201,0.06) 0%,transparent 50%); }
.hero-content { position:relative; text-align:center; max-width:720px; }
.badge { display:inline-block; padding:6px 16px; background:rgba(108,92,231,0.08); color:#6C5CE7; border-radius:20px; font-size:13px; font-weight:600; margin-bottom:24px; }
.hero-content h1 { font-size:56px; font-weight:800; line-height:1.1; margin-bottom:20px; letter-spacing:-1.5px; }
.gradient { background:linear-gradient(135deg,#6C5CE7,#00CEC9); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.hero-content p { font-size:18px; color:#636E70; line-height:1.6; margin-bottom:32px; max-width:560px; margin-left:auto; margin-right:auto; }
.hero-actions { display:flex; gap:12px; justify-content:center; }
.btn-primary { padding:14px 32px; background:#6C5CE7; color:#fff; border:none; border-radius:10px; font-size:15px; font-weight:600; cursor:pointer; text-decoration:none; display:inline-block; }
.btn-primary:hover { background:#5A4BD1; }
.btn-ghost { padding:14px 32px; border:1.5px solid #DFE6E9; border-radius:10px; color:#1A1A2E; font-size:15px; font-weight:500; cursor:pointer; text-decoration:none; display:inline-block; }
.btn-ghost:hover { border-color:#6C5CE7; }
.features { padding:100px 40px; text-align:center; max-width:1100px; margin:0 auto; }
.features h2 { font-size:36px; font-weight:700; line-height:1.2; margin-bottom:60px; }
.feature-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:24px; }
.feature-card { background:#fff; border:1px solid #E8EAED; border-radius:14px; padding:28px; text-align:left; }
.feature-card .icon { width:44px; height:44px; border-radius:10px; background:rgba(108,92,231,0.08); color:#6C5CE7; display:flex; align-items:center; justify-content:center; margin-bottom:16px; }
.feature-card h3 { font-size:17px; font-weight:600; margin-bottom:8px; }
.feature-card p { font-size:14px; color:#636E70; line-height:1.5; }
.pricing { padding:100px 40px; text-align:center; }
.pricing h2 { font-size:36px; font-weight:700; margin-bottom:48px; }
.pricing-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; max-width:960px; margin:0 auto; }
.plan { background:#fff; border:1px solid #E8EAED; border-radius:14px; padding:32px; text-align:left; position:relative; }
.plan.popular { border-color:#6C5CE7; box-shadow:0 4px 20px rgba(108,92,231,0.1); }
.pop-badge { position:absolute; top:-12px; left:50%; transform:translateX(-50%); padding:4px 14px; background:#6C5CE7; color:#fff; border-radius:20px; font-size:12px; font-weight:600; }
.plan h3 { font-size:20px; font-weight:700; margin-bottom:4px; }
.price { font-size:36px; font-weight:800; margin-bottom:20px; }
.price span { font-size:16px; color:#636E70; font-weight:400; }
.plan ul { list-style:none; padding:0; margin-bottom:24px; }
.plan ul li { padding:8px 0; font-size:14px; color:#636E70; position:relative; padding-left:24px; }
.plan ul li::before { content:'✓'; position:absolute; left:0; color:#00B894; font-weight:700; }
.plan .btn-primary { width:100%; text-align:center; }
.footer { border-top:1px solid #E8EAED; padding:40px; }
.footer-inner { max-width:1100px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; }
.footer-brand { display:flex; align-items:center; gap:8px; font-weight:600; }
.footer-links { display:flex; gap:20px; }
.footer-links a { color:#636E70; text-decoration:none; font-size:14px; }
.footer-links a:hover { color:#1A1A2E; }
.footer-copy { font-size:13px; color:#B2BEC3; }
@media (max-width:768px) {
  .feature-grid { grid-template-columns:1fr; }
  .pricing-grid { grid-template-columns:1fr; }
  .hero-content h1 { font-size:36px; }
}
</style>