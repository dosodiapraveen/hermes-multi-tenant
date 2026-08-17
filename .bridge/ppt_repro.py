import sys, os
sys.path.insert(0, "/app")
from app.routers.webhook import try_build_deck

deck_path = ("/opt/hermes/hermes/profiles/4fee15b6-e1a7-4a90-8b81-913fd6a19a74/skills/"
             "productivity/powerpoint/scripts/second_opinion_deck.json")
raw = open(deck_path).read().rstrip("\n")
# Reconstruct exactly the unified-diff the agent emitted to the user:
path = "profiles/4fee15b6-e1a7-4a90-8b81-913fd6a19a74/skills/productivity/powerpoint/scripts/second_opinion_deck.json"
diff = (f"a/{path} → b/{path}\n"
        "@@ -0,0 +1,194 @@\n" +
        "\n".join("+" + ln for ln in raw.split("\n")) )
print("DIFF_LEN", len(diff))
res = try_build_deck(diff)
print("TRY_BUILD_DECK_RESULT:", repr(res)[:120])
res2 = try_build_deck(raw)
print("CLEAN_JSON_RESULT:", repr(res2)[:120])
