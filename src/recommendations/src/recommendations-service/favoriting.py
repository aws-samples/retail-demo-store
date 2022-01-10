
username_to_product_favorites = dict()


def set_favorited(username, product_id, value):
    """
    Adds the product in question as favorited by user.
    Args:
        username (str): user to favorite the product
        product_id (str): id of favorited product

    Returns:

    """
    nres = 0
    if value:
        user_favorites = username_to_product_favorites.setdefault(username, set())
        if product_id not in user_favorites:
            user_favorites.add(product_id)
            nres += 1
    else:
        if username in username_to_product_favorites:
            user_favorites = username_to_product_favorites[username]
            if product_id in user_favorites:
                nres -= 1
            user_favorites.remove(product_id)
            if len(user_favorites) == 0:
                del username_to_product_favorites[username]
    return nres


def favorited_products(username):
    """
    All products favorited by this user
    Args:
        username (str): user to favorite the product

    Returns:
        list[str]: list of product IDs favorited
    """
    return username_to_product_favorites.get(username, set())


def is_favorited(username, product_id):
    """
    Tells us whether the product in question is favorited by the user.
    Args:
        username (str): user to favorite the product
        product_id (str): id of favorited product

    Returns:
        bool: is it?
    """
    return product_id in favorited_products(username)


# def user_segments(username):
#     ##Temporary code to test front end with - move to Neptune backend
#     MARKETING_SEGMENTS = ('Promotion Hunter', 'Digital Native', 'High Value Customer', 'Winback Customer')
#     import random
#     pass
#     if username == 'lanawilliams625':
#         segments = ["High Value Customer", "Winback Customer", "Digital Native"]
#     else:
#         segments = random.sample(MARKETING_SEGMENTS, random.randint(0, len(MARKETING_SEGMENTS)-1))
#     return segments

def get_c360_alerts(username):
    ##Temporary code to test front end with - to move to Neptune backend
    messages = []
    if username == 'lanawilliams625':
        pr = False
        for p in favorited_products(username):
            pr = True

        if pr:
            message = """
Dear Lana,

This product is low in stock!

As you are a valued customer of Retail Demo Store, we would like to offer you to place this product 
JunkyJunkyWhatnot on a watchlist so that you can be notified if or when it comes back in stock.

Kind regards,
Retail Demo Store
            """
            subject = 'Low stock product!'
            messages.append({'text': message, 'subject': subject})
    return messages


