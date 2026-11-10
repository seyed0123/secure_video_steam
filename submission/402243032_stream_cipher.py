"""Small, deliberately insecure LFSR stream cipher for teaching."""

MAX_SEED = 0xFFFF
LFSR_PERIOD_BITS = 0xFFFF


def _validate_seed(seed: int) -> None:
    if not isinstance(seed, int) or not 1 <= seed <= MAX_SEED:
        raise ValueError("seed must be an integer from 1 to 65535")


def _next_bit(state: int) -> tuple[int, int]:
    """Return output bit and next state for x^16 + x^14 + x^13 + x^11 + 1."""
    output = state & 1
    feedback = ((state >> 0) ^ (state >> 2) ^ (state >> 3) ^ (state >> 5)) & 1
    return output, (state >> 1) | (feedback << 15)


def keystream(length: int, seed: int, offset: int = 0) -> bytes:
    """Return length keystream bytes, starting at an absolute byte offset."""
    _validate_seed(seed)
    if not isinstance(length, int) or length < 0:
        raise ValueError("length must be a non-negative integer")
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a non-negative integer")

    state = seed
    # Reduce bit skips by the maximal bit period, not by 8192 bytes.
    for _ in range((offset * 8) % LFSR_PERIOD_BITS):
        _, state = _next_bit(state)
    result = bytearray(length)
    for index in range(length):
        value = 0
        for _ in range(8):
            bit, state = _next_bit(state)
            value = (value << 1) | bit
        result[index] = value
    return bytes(result)


def xor_bytes(data: bytes, seed: int, offset: int = 0) -> bytes:
    """Encrypt or decrypt data with the keystream at absolute byte offset."""
    return bytes(value ^ key for value, key in zip(data, keystream(len(data), seed, offset)))
