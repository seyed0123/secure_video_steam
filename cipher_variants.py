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
    def step(state: int) -> tuple[int, int]:
        feedback = (state ^ (state >> 2) ^ (state >> 3) ^ (state >> 5)
                    ^ ((state >> 1) & (state >> 7))) & 1
        return state & 1, (state >> 1) | (feedback << 15)

    state = seed
    remaining = offset * 8
    seen = {}
    while remaining:
        if state in seen:
            remaining %= seen[state] - remaining
            seen.clear()
            if not remaining:
                break
        seen[state] = remaining
        _, state = step(state)
        remaining -= 1

    result = bytearray(length)
    for i in range(length):
        value = 0
        for _ in range(8):
            bit, state = step(state)
            value = (value << 1) | bit
        result[i] = value
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
    states = list(seeds)
    for _ in range((offset * 8) % LFSR_PERIOD_BITS):
        for i in range(3):
            _, states[i] = _next_bit(states[i])

    result = bytearray(length)
    for i in range(length):
        value = 0
        for _ in range(8):
            x, states[0] = _next_bit(states[0])
            y, states[1] = _next_bit(states[1])
            z, states[2] = _next_bit(states[2])
            value = (value << 1) | ((x & y) ^ ((1 ^ x) & z))
        result[i] = value
    return bytes(result)
