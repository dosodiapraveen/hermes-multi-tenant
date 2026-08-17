import sys, os
sys.path.insert(0, "/app")
from app.routers.webhook import try_build_deck

# 1) find the deck file the agent produced for the Test Deck request
for cand in ("/tmp/second_opinion_deck.json",
             "/opt/hermes/hermes/profiles/4fee15b6-e1a7-4a90-8b81-913fd6a19a74/skills/productivity/powerpoint/scripts/second_opinion_deck.json"):
    if os.path.exists(cand):
        raw = open(cand).read()
        print("deck file:", cand, "len", len(raw))
        # 2) reconstruct the diff-wrapped agent reply WITH the noise that breaks naive parsing
        body = raw.rstrip("\n")
        reply = (f"a//tmp/second_opinion_deck.json -> b//tmp/second_opinion_deck.json\n"
                 f"@@ -0,0 +1,{body.count(chr(10))+1} @@\n"
                 + "\n".join("+" + l for l in body.split("\n")) + "\n"
                 f"\\ No newline at end of file\n"
                 f"Here is the deck I created above.")
        out = try_build_deck(reply)
        print("REALISTIC_DIFF ->", out, "EXISTS:", bool(out and os.path.exists(out)))
        # 3) plain-form
        print("PLAIN ->", try_build_deck(raw))
        break
else:
    print("no deck file found")
