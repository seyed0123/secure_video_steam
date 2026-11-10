"""Small, deliberately insecure LFSR stream cipher for teaching."""

MAX_SEED = 0xFFFF
LFSR_PERIOD_BITS = 0xFFFF


def _validate_seed(seed: int) -> None:
    if not isinstance(seed, int) or not 1 <= seed <= MAX_SEED:
        raise ValueError("seed must be an integer from 1 to 65535")


def _next_bit(state: int) -> tuple[int, int]:
    """Return output bit and next state for x^16 + x^14 + x^13 + x^11 + 1."""
    out = state & 1
    fb = (state ^ (state >> 2) ^ (state >> 3) ^ (state >> 5)) & 1
    state = (state >> 1) | (fb << 15)
    return out, state


def keystream(length: int, seed: int, offset: int = 0) -> bytes:
    """Return length keystream bytes, starting at an absolute byte offset."""
    _validate_seed(seed)
    if not isinstance(length, int) or length < 0:
        raise ValueError("length must be a non-negative integer")
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a non-negative integer")

    state = seed
    for _ in range((offset * 8) % LFSR_PERIOD_BITS):
        _, state = _next_bit(state)

    out = bytearray(length)
    for i in range(length):
        byte = 0
        for _ in range(8):
            bit, state = _next_bit(state)
            byte = (byte << 1) | bit
        out[i] = byte
    return bytes(out)


def xor_bytes(data: bytes, seed: int, offset: int = 0) -> bytes:
    """Encrypt or decrypt data with the keystream at absolute byte offset."""
    data = bytes(data)
    ks = keystream(len(data), seed, offset)
    x = int.from_bytes(data, "big") ^ int.from_bytes(ks, "big")
    return x.to_bytes(len(data), "big")