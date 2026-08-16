import subprocess, json, time, urllib.request, urllib.error, re
shell=True
def run(c): 
    p=subprocess.run(c,shell=True,capture_output=True,text=True); return p.stdout.strip(), p.stderr.strip(), p.returncode
UID="ddd0a001-0000-4000-8000-00000000f001"; EMAIL="tzt@throwaway.dev"; PW="TzTest2026!"
PG="hermes-multi-tenant-postgres-1"; API="hermes-multi-tenant-api-1"; B="https://beprepared.dev"
# setup throwaway profile+account
hpw=run(f"docker exec {API} python3 -c \"import bcrypt;print(bcrypt.hashpw(b'{PW}',bcrypt.gensalt()).decode())\"")[0]
sql=f"""INSERT INTO user_profiles (id,agent_name,phone_number,platform,is_active) VALUES ('{UID}','TzTester','9990000060','telegram',true) ON CONFLICT (id) DO NOTHING;
INSERT INTO user_accounts (user_profile_id,email,password_hash,email_verified) VALUES ('{UID}','{EMAIL}','{hpw}',true) ON CONFLICT DO NOTHING;"""
open("/tmp/tz.sql","w").write(sql)
run(f"scp -i /root/.ssh/* /tmp/tz.sql root@127.0.0.1:/tmp 2>/dev/null") # noop
out=run(f"cp /tmp/tz.sql /root/.hermes/bridge 2>/dev/null; docker cp /tmp/tz.sql {PG}:/tmp 2>/dev/null")[0]
print("sql staged")
print(run(f"docker exec -i {PG} psql -U hermes < /tmp/tz.sql 2>&1")[0])
