from typing import Tuple, List

from chia.util.ints import uint64


def get_new_difficulty(
    recent_partials: List[Tuple[uint64, uint64]],
    number_of_partials_target: int,
    time_target: int,
    current_difficulty: uint64,
    custom_difficulty: str,
    current_time: uint64,
    min_difficulty: uint64,
) -> uint64:
    """
    Given the last number_of_partials_target (or total partials we have) from a given farmer, return the new
    difficulty, or the same difficulty if we do not want to update.
    """

    # Return fixed difficulty if custom difficulty with EXPERT is set
    if custom_difficulty is not None and custom_difficulty.startswith('EXPERT:'):
        return int(custom_difficulty[7:])

    # If we haven't processed any partials yet, maintain the current (default) difficulty
    if len(recent_partials) == 0:
        return current_difficulty

    # If we recently updated difficulty, don't update again
    if any(difficulty != current_difficulty for timestamp, difficulty in recent_partials):
        return current_difficulty

    # Lower the difficulty if we are really slow since our last partial
    last_timestamp = recent_partials[0][0]
    if current_time - last_timestamp > 3 * 3600:
        return uint64(max(min_difficulty, current_difficulty // 5))

    if current_time - last_timestamp > 3600:
        return uint64(max(min_difficulty, uint64(int(current_difficulty / 1.5))))

    time_taken = (recent_partials[0][0] - recent_partials[-1][0]) * 1.0

    if custom_difficulty == 'LOWEST':
        number_of_partials_target = int(number_of_partials_target * 2)
    elif custom_difficulty == 'LOW':
        number_of_partials_target = int(number_of_partials_target * 1.5)
    elif custom_difficulty == 'MEDIUM':
        pass
    elif custom_difficulty == 'HIGH':
        number_of_partials_target = int(number_of_partials_target * 0.75)
    elif custom_difficulty == 'HIGHEST':
        number_of_partials_target = int(number_of_partials_target * 0.5)
    elif custom_difficulty is not None and custom_difficulty.startswith('CUSTOM:'):
        number_of_partials_target = int(custom_difficulty[7:])
    elif custom_difficulty:
        raise RuntimeError(custom_difficulty)

    # If we don't have enough partials at this difficulty and time between last and
    # 1st partials is below target time, don't update yet
    if len(recent_partials) < number_of_partials_target and time_taken < time_target * 0.8:
        return current_difficulty

    # Adjust time_taken if number of partials didn't reach number_of_partials_target
    if len(recent_partials) < number_of_partials_target:
        time_taken = time_taken * number_of_partials_target / len(recent_partials)

    # Adjust time_taken if we changed custom difficulty and we are getting 50% more partials than we should
    if len(recent_partials) > number_of_partials_target * 1.5:
        time_taken = time_taken * number_of_partials_target / len(recent_partials)

    # Finally, this is the standard case of normal farming and slow (or no) growth, adjust to the new difficulty

    new_difficulty = uint64(int(current_difficulty * time_target / time_taken))

    return uint64(max(min_difficulty, new_difficulty))
