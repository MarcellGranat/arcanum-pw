from src.user import next_user_cycle


def test_cycle() -> None:
    print("Cycle started")
    for user in next_user_cycle():
        assert user.username
