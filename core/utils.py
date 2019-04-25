import random
from .models import User


def create_temporary_user(verifier):
    username = f'user_{"".join(list(map(str, [random.randint(0, 9) for _ in range(0, 9)])))}'
    while User.objects.filter(username=username).count() != 0:
        print("somehow got a duplicate number lol")
        username = f'user_{"".join(list(map(str, [random.randint(0, 9) for _ in range(0, 9)])))}'

    user = User.objects.create(username=username, verifier=verifier)
    user.save()
    return user
