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
    state = seed
    skip_bits = offset * 8
    for _ in range(skip_bits):
        nl_term = ((state >> 1) & 1) & ((state >> 7) & 1)
        feedback = (((state >> 0) ^ (state >> 2) ^ (state >> 3) ^ (state >> 5)) ^ nl_term) & 1
        state = (state >> 1) | (feedback << 15)

    result = bytearray(length)
    for byte_idx in range(length):
        b = 0
        for _ in range(8):
            out_bit = state & 1
            nl_term = ((state >> 1) & 1) & ((state >> 7) & 1)
            feedback = (((state >> 0) ^ (state >> 2) ^ (state >> 3) ^ (state >> 5)) ^ nl_term) & 1
            state = (state >> 1) | (feedback << 15)
            b = (b << 1) | out_bit
        result[byte_idx] = b
    return bytes(result)


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
    s1, s2, s3 = seeds
    skip_bits = (offset * 8) % LFSR_PERIOD_BITS
    for _ in range(skip_bits):
        fb1 = ((s1 >> 0) ^ (s1 >> 2) ^ (s1 >> 3) ^ (s1 >> 5)) & 1
        s1 = (s1 >> 1) | (fb1 << 15)
        fb2 = ((s2 >> 0) ^ (s2 >> 2) ^ (s2 >> 3) ^ (s2 >> 5)) & 1
        s2 = (s2 >> 1) | (fb2 << 15)
        fb3 = ((s3 >> 0) ^ (s3 >> 2) ^ (s3 >> 3) ^ (s3 >> 5)) & 1
        s3 = (s3 >> 1) | (fb3 << 15)

    result = bytearray(length)
    for byte_idx in range(length):
        b = 0
        for _ in range(8):
            x = s1 & 1
            fb1 = ((s1 >> 0) ^ (s1 >> 2) ^ (s1 >> 3) ^ (s1 >> 5)) & 1
            s1 = (s1 >> 1) | (fb1 << 15)

            y = s2 & 1
            fb2 = ((s2 >> 0) ^ (s2 >> 2) ^ (s2 >> 3) ^ (s2 >> 5)) & 1
            s2 = (s2 >> 1) | (fb2 << 15)

            z = s3 & 1
            fb3 = ((s3 >> 0) ^ (s3 >> 2) ^ (s3 >> 3) ^ (s3 >> 5)) & 1
            s3 = (s3 >> 1) | (fb3 << 15)

            out_bit = (x & y) ^ ((1 ^ x) & z)
            b = (b << 1) | out_bit
        result[byte_idx] = b
    return bytes(result)

