"""Student exercises for nonlinear stream-generator variants."""

from stream_cipher import LFSR_PERIOD_BITS, MAX_SEED, _next_bit

DEFAULT_GEFFE_SEEDS = (0xACE1, 0xBEEF, 0x1234)


def _validate(length: int, seeds: tuple[int, ...], offset: int) -> None:
    if not isinstance(length, int) or length < 0:
        raise ValueError("length must be a non-negative integer")
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a non-negative integer")
    if any(not isinstance(seed, int) or not 1 <= seed <= MAX_SEED for seed in seeds):
        raise ValueError("every seed must be an integer from 1 to 65535")


def nlfsr_keystream(length: int, seed: int, offset: int = 0) -> bytes:
    """Generate bytes from an NLFSR with one nonlinear AND feedback term.

    Use the base feedback bits 0, 2, 3, and 5, then XOR them with
    (bit 1 AND bit 7). Output, shifting, offset, and packing match the LFSR.
    """
    _validate(length, (seed,), offset)
    # TODO(student 7): replace this reference NLFSR in the handout.
    period = 0xFFFF
    state = seed

    def step(s: int) -> tuple[int, int]:
        output = s & 1
        linear = ((s >> 0) ^ (s >> 2) ^ (s >> 3) ^ (s >> 5)) & 1
        nonlinear = ((s >> 1) & 1) & ((s >> 7) & 1)   # bit 1 AND bit 7
        feedback = (linear ^ nonlinear) & 1
        return output, (s >> 1) | (feedback << 15)

    for _ in range((offset * 8) % period):
        _, state = step(state)

    out = bytearray()
    for _ in range(length):
        byte = 0
        for _ in range(8):
            bit, state = step(state)
            byte = (byte << 1) | bit
        out.append(byte)
    return bytes(out)


def geffe_keystream(
    length: int,
    seeds: tuple[int, int, int] = DEFAULT_GEFFE_SEEDS,
    offset: int = 0,
) -> bytes:
    """Combine three LFSR output bits with the nonlinear Geffe function.

    If the three output bits are x, y, and z, emit
    (x AND y) XOR ((1 XOR x) AND z). Each component uses the base LFSR.
    """
    if len(seeds) != 3:
        raise ValueError("the Geffe generator needs exactly three seeds")
    _validate(length, seeds, offset)
    # TODO(student 8): replace this reference Geffe generator in the handout.

    period = 0xFFFF
    s1, s2, s3 = seeds

    def step(s: int) -> tuple[int, int]:
        output = s & 1
        feedback = ((s >> 0) ^ (s >> 2) ^ (s >> 3) ^ (s >> 5)) & 1
        return output, (s >> 1) | (feedback << 15)

    for _ in range((offset * 8) % period):
        _, s1 = step(s1)
        _, s2 = step(s2)
        _, s3 = step(s3)

    out = bytearray()
    for _ in range(length):
        byte = 0
        for _ in range(8):
            x, s1 = step(s1)
            y, s2 = step(s2)
            z, s3 = step(s3)
            # Geffe: (x AND y) XOR ((1 XOR x) AND z)
            bit = (x & y) ^ ((1 ^ x) & z)
            byte = (byte << 1) | (bit & 1)
        out.append(byte)
    return bytes(out)
