import sys, os, json
sys.path.insert(0, "/app")
from app.routers.webhook import try_build_deck, build_pptx

# find the real deck the agent produced
found = None
for path in ["/root/second_opinion/deck_spec.json", "/tmp/second_opinion_deck.json",
             "/opt/hermes/hermes/profiles/4fee15b6-e1a7-4a90-8b81-913fd6a19a74/skills/productivity/powerpoint/scripts/second_opinion_deck.json"]:
    if os.path.exists(path):
        found = path; break
print("DECK_FILE:", found)
if not found:
    sys.exit("none")
raw = open(found).read()
# reconstruct the exact agent reply: leading '┊ review diff' + diff + trailing prose
body = raw.rstrip("\n")
reply = ("┊ review diff\n"
         "a//root/second_opinion/deck_spec.json → b//root/second_opinion/deck_spec.json\n"
         f"@@ -0,0 +1,{body.count(chr(10))+1} @@\n"
         + "\n".join("+"+l for l in body.split("\n")) + "\n"
         "\\ No newline at end of file\n"
         "Want me to turn this into a PDF, split it into a printable one-pager, or draft the questionnaire?")

out = try_build_deck(reply)
print("try_build_deck(realistic):", out, "EXISTS:", bool(out and os.path.exists(out)))

# replicate brace-extraction to see the actual JSON error
clean = "\n".join((l[1:] if l.startswith("+") else l) for l in reply.splitlines()
                  if l.strip() and not l.startswith(("@", "a/", "b/", "diff ", "index ", "\\")))
i, j = clean.find("{"), clean.rfind("}")
print("brace i,j:", i, j, "cleanlen:", len(clean))
try:
    d = json.loads(clean[i:j+1])
    print("json.loads OK, slides:", len(d.get("slides", [])))
except Exception as e:
    print("JSON_PARSE_ERROR:", repr(e))
    print("segment start:", repr(clean[i:i+120]))
    print("segment end:", repr(clean[j-120:j+1]))
