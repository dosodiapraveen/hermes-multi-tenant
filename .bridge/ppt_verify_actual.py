import sys, os, json, glob
sys.path.insert(0, "/app")
from app.routers.webhook import try_build_deck

# find the ACTUAL deck files produced by recent runs
files = []
for pat in ["/root/second_opinion/*.json", "/tmp/deck_in_*.json", "/tmp/second_opinion_deck.json",
            "/opt/hermes/hermes/profiles/*/skills/productivity/powerpoint/scripts/*.json",
            "/opt/hermes/hermes/profiles/*/work/*.json"]:
    files += glob.glob(pat)
files = list(dict.fromkeys(files))
print("ACTUAL deck candidates:", files[:6])
for f in files[:4]:
    if not os.path.exists(f): continue
    raw = open(f).read()
    print("---", f, "len", len(raw))
    # reconstruct the diff reply exactly as the agent emits it
    body = raw.rstrip("\n")
    reply = ("┊ review diff\n"
             f"a//root/second_opinion/{(os.path.basename(f))} → b//root/...{(os.path.basename(f))}\n"
             f"@@ -0,0 +1,{body.count(chr(10))+1} @@\n"
             + "\n".join("+"+l for l in body.split("\n")) + "\n"
             "\\ No newline at end of file\n"
             "Want me to turn this into a PDF, split it into a printable one-pager, or draft the questionnaire?")
    out = try_build_deck(reply)
    print("try_build_deck(actual-diff):", out, "EXISTS:", bool(out and os.path.exists(out)))
