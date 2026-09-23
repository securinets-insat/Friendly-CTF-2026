#!/usr/bin/env python3
"""Service-side reference for the game-track token.

This is the half the quiz service runs. The game emits f(nonce, state); this
recomputes it and decides whether to hand back a flag. The flag never appears
here either -- that lives in the service's environment, same as case 01's.

The message format is load-bearing and must match src/challenge.c exactly:

    cgv1|<game_id>|<nonce>|cleared

Bound fields, and why each one is in there:
  game_id  a token minted for game 1 must not unlock game 2
  nonce    per-player, so a posted token is worthless to anyone else

The exact score is deliberately NOT in the message, and this was a considered
reversal. Binding it meant the service had to search the score space to verify a
one-field submission -- ~300k HMACs per attempt, which is a free DoS on an endpoint
that must accept unauthenticated input. It bought nothing: the score is not a secret
and never proved anything on its own. What proves the clamped-out state is that the
native side refuses to emit a token below CG_TOKEN_MIN at all. Forging still costs
the attacker the key, exactly as before.

Consequence to know: the token is constant per (game_id, nonce). It is still per
player, so sharing it is still useless to anyone else.
"""
import argparse
import hmac
import hashlib

TOKEN_GROUPS = 5
TOKEN_BYTES = TOKEN_GROUPS * 2
SCORE_CLAMP = 99999
TOKEN_MIN = SCORE_CLAMP + 1
NONCE_MAX = 32


def normalize_nonce(nonce: str) -> str:
    return nonce.strip().upper()


def nonce_ok(nonce: str) -> bool:
    if not nonce or len(nonce) > NONCE_MAX:
        return False
    return all(c.isdigit() or ("A" <= c <= "Z") or c == "-" for c in nonce)


def make_token(key: bytes, game_id: int, nonce: str) -> str:
    """Compute the token the game emits once the player is above the clamp."""
    msg = f"cgv1|{game_id}|{nonce}|cleared".encode()
    mac = hmac.new(key, msg, hashlib.sha256).digest()[:TOKEN_BYTES]
    hexed = mac.hex().upper()
    return "-".join(hexed[i:i + 4] for i in range(0, len(hexed), 4))


def verify(key: bytes, game_id: int, nonce: str, submitted: str) -> bool:
    """True if `submitted` is the token this player's game would emit. O(1)."""
    nonce = normalize_nonce(nonce)
    if not nonce_ok(nonce):
        return False
    return hmac.compare_digest(make_token(key, game_id, nonce), submitted.strip().upper())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True, help="hex key, or a path to a key file")
    ap.add_argument("--game-id", type=int, required=True)
    ap.add_argument("--nonce", required=True)
    sub = ap.add_mutually_exclusive_group(required=True)
    sub.add_argument("--mint", action="store_true", help="print the expected token")
    sub.add_argument("--verify", help="check a submitted token")
    args = ap.parse_args()

    raw = args.key
    try:
        key = bytes.fromhex(raw)
    except ValueError:
        key = bytes.fromhex(open(raw).read().strip())

    nonce = normalize_nonce(args.nonce)
    if args.mint:
        print(make_token(key, args.game_id, nonce))
    else:
        print("VALID" if verify(key, args.game_id, nonce, args.verify) else "INVALID")


if __name__ == "__main__":
    main()
