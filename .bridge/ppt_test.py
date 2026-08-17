import sys, os, json
sys.path.insert(0, "/app")
import pptx
from app.routers.webhook import try_build_deck, build_pptx
print("pptx ok:", pptx.__version__)
deck = {
    "title": "The Second Opinion in Indian Healthcare",
    "slide_size": "16:9",
    "slides": [
        {"layout": "title", "title": "Title slide", "content": ["Avenues", "Hurdles", "Who is solving", "Is there a business"]},
        {"layout": "title_content", "title": "Why this matters", "content": ["Market context", "Growth data", "Economics"]},
    ],
}
deck_json = json.dumps(deck)
# diff-wrapped form the agent emitted for Prav
lines = [l for l in deck_json.splitlines()]
diff_wrapped = "a//tmp/deck.json → b//tmp/deck.json\n@@ -0,0 +1,%d @@\n" % len(lines) + "\n".join("+" + l for l in lines) + "\n"
p = try_build_deck(diff_wrapped)
print("DIFF_WRAPPED_PPTX:", p, "size", os.path.getsize(p) if p else 0)
p2 = build_pptx(deck)
print("PLAIN_PPTX_SIZE:", os.path.getsize(p2) if p2 else 0)
