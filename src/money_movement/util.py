import random
import string


def generate_random_id(length: int = 8) -> str:
    """
    Generate a random ID of a given length. Could expand with uuid.
    """
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
