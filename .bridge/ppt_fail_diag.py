import sys, os, json
sys.path.insert(0, "/app")
from app.routers.webhook import try_build_deck, build_pptx

cands = [
    "/tmp/second_opinion_deck.json",
    "/opt/hermes/hermes/profiles/4fee15b6-e1a7-4a90-8b81-913fd6a19a74/skills/productivity/powerpoint/scripts/second_opinion_deck.json",
]
for c in cands:
    if os.path.exists(c):
        raw = open(c).read()
        print("FOUND:", c, "len", len(raw))
        # what does try_build_deck do with the raw file?
        print("try_build_deck(raw):", try_build_deck(raw))
        # build_pptx on parsed deck
        try:
            d = json.loads(raw)
            print("parsed slides:", len(d.get("slides", [])), "title:", d.get("title"))
            print("build_pptx:", build_pptx(d))
        except Exception as e:
            print("parse/build error:", repr(e))
        break
else:
    print("NO deck files found")
