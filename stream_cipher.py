"""Small, deliberately insecure LFSR stream cipher for teaching."""

MAX_SEED = 0xFFFF
LFSR_PERIOD_BITS = 0xFFFF


def _validate_seed(seed: int) -> None:
    if not isinstance(seed, int) or not 1 <= seed <= MAX_SEED:
        raise ValueError("seed must be an integer from 1 to 65535")


def _next_bit(state: int) -> tuple[int, int]:
    """Return output bit and next state for x^16 + x^14 + x^13 + x^11 + 1."""
    # TODO(student 1): replace this reference state transition in the handout.
    out = state & 1
    fb = (state ^ (state >> 2) ^ (state >> 3) ^ (state >> 5)) & 1
    return out, (state >> 1) | (fb << 15)


def keystream(length: int, seed: int, offset: int = 0) -> bytes:
    """Return length keystream bytes, starting at an absolute byte offset."""
    _validate_seed(seed)
    if not isinstance(length, int) or length < 0:
        raise ValueError("length must be a non-negative integer")
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a non-negative integer")

    # TODO(student 2): replace this reference generator in the handout.
    state = seed
    skip = (offset * 8) % LFSR_PERIOD_BITS
    for _ in range(skip):
        _, state = _next_bit(state)
    out = bytearray()
    for _ in range(length):
        byte = 0
        for _ in range(8):
            bit, state = _next_bit(state)
            byte = (byte << 1) | bit
        out.append(byte)
    return bytes(out)


def xor_bytes(data: bytes, seed: int, offset: int = 0) -> bytes:
    """Encrypt or decrypt data with the keystream at absolute byte offset."""
    # TODO(student 3): replace this reference XOR operation in the handout.
    ks = keystream(len(data), seed, offset)
    return bytes(a ^ b for a, b in zip(data, ks))
