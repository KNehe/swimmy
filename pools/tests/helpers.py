from pools.models import Pool, User


def create_test_user(email="nehe@gmail.com"):
    """
    Creates and returns a user object to be used in different unit tests
    """
    user = User.objects.create(email=email, password="123Deaally@", username=email)
    return user


def create_test_pool(user=None):
    """
    Creates and returns a swimmming pool
    object to be used in different unit tests
    """
    user = user if user else create_test_user()
    pool = Pool.objects.create(
        created_by=user,
        name="Nehe Ducks",
        location="Naboa road Mbale uganda",
        day_price=10.0,
        thumbnail_url="https://aws.s3/images/pic.png",
        image_url="https://aws.s3/images/pic.png",
        width=4.0,
        length=8.2,
        depth_shallow_end=1.2,
        depth_deep_end=3.0,
        maximum_people=15,
    )
    return pool
