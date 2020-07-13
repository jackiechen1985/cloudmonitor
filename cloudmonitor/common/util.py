import random
import string


def random_string(length):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))
