"""Small, deliberately insecure LFSR stream cipher for teaching."""

MAX_SEED = 0xFFFF
LFSR_PERIOD_BITS = 0xFFFF


def _validate_seed(seed: int) -> None:
    if not isinstance(seed, int) or not 1 <= seed <= MAX_SEED:
        raise ValueError("seed must be an integer from 1 to 65535")


def _next_bit(state: int) -> tuple[int, int]:
    """Return output bit and next state for x^16 + x^14 + x^13 + x^11 + 1."""
    # TODO(student 1): replace this reference state transition in the handout.
    state &= MAX_SEED
    output_bit = state & 1

    # Fibonacci feedback: taps at bit positions 0, 2, 3, and 5.
    feedback = (
        ((state >> 0) & 1)
        ^ ((state >> 2) & 1)
        ^ ((state >> 3) & 1)
        ^ ((state >> 5) & 1)
    )
    next_state = (state >> 1) | (feedback << 15)
    return output_bit, next_state & MAX_SEED


def keystream(length: int, seed: int, offset: int = 0) -> bytes:
    """Return length keystream bytes, starting at an absolute byte offset."""
    _validate_seed(seed)
    if not isinstance(length, int) or length < 0:
        raise ValueError("length must be a non-negative integer")
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a non-negative integer")

    # TODO(student 2): replace this reference generator in the handout.
    state = seed
    # One byte consumes eight LFSR steps. Offset is an absolute byte offset.
    for _ in range((offset * 8) % LFSR_PERIOD_BITS):
        _, state = _next_bit(state)

    output = bytearray()
    for _ in range(length):
        value = 0
        for _ in range(8):
            bit, state = _next_bit(state)
            value = (value << 1) | bit
        output.append(value)
    return bytes(output)


def xor_bytes(data: bytes, seed: int, offset: int = 0) -> bytes:
    """Encrypt or decrypt data with the keystream at absolute byte offset."""
    # TODO(student 3): replace this reference XOR operation in the handout.
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("data must be bytes-like")
    key = keystream(len(data), seed, offset)
    return bytes(value ^ key_byte for value, key_byte in zip(data, key))
