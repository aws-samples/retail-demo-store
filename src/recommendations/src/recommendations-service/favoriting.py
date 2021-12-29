
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


def user_segments(username):
    ##Temporary code to test front end with
    pass