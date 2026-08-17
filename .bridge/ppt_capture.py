import asyncio, sys, os
sys.path.insert(0, "/app")
from app.routers.webhook import run_hermes_runtime, try_build_deck

Q = ("perform research on indian healthcare system for the aspect of getting a second opinion. "
     "what are the avenues, what are the hurdles? Anyone solving this issue? Is there a business to be made. "
     "If yes, how to go about it. Make a slideshow about this")

resp = asyncio.run(run_hermes_runtime("4fee15b6-e1a7-4a90-8b81-913fd6a19a74", Q))
print("RESP_LEN:", len(resp or ""))
print("RESP_HEAD:", repr((resp or "")[:300]))
print("RESP_TAIL:", repr((resp or "")[-200:]))
print("HAS_slides:", 'slides' in (resp or ''))
print("HAS_a/:", resp and resp.lstrip().startswith('a/'))
deck = try_build_deck(resp) if resp else None
print("TRY_BUILD_DECK:", deck, "EXISTS:", bool(deck and os.path.exists(deck)))
