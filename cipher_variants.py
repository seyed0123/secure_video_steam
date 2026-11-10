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

    def step(current: int) -> tuple[int, int]:
        feedback = (
            current ^ (current >> 2) ^ (current >> 3) ^ (current >> 5)
            ^ (((current >> 1) & 1) & ((current >> 7) & 1))
        ) & 1
        return current & 1, (current >> 1) | (feedback << 15)

    # The nonlinear register does not inherit the LFSR's 65535-bit period.
    for _ in range(offset * 8):
        _, state = step(state)
    result = bytearray(length)
    for index in range(length):
        value = 0
        for _ in range(8):
            bit, state = step(state)
            value = (value << 1) | bit
        result[index] = value
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
        states = [_next_bit(state)[1] for state in states]
    result = bytearray(length)
    for index in range(length):
        value = 0
        for _ in range(8):
            x, states[0] = _next_bit(states[0])
            y, states[1] = _next_bit(states[1])
            z, states[2] = _next_bit(states[2])
            bit = (x & y) ^ ((1 ^ x) & z)
            value = (value << 1) | bit
        result[index] = value
    return bytes(result)
