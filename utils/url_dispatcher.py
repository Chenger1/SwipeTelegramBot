# Contains all the relative paths for SwipeRestApi
REL_URLS = {
    'login': 'auth/login/',

    # PUBLIC - Don`t require auth token
    'posts_public': 'main/posts_public/',
    'houses_public': 'main/houses_public/',
    'flats_public': 'main/flats_public/',

    # COMPLAINT
    'complaint': 'main/complaints/',

    # FAVORITES
    'favorites': 'main/favorites_posts/',

    #NEWS
    'news': 'main/news/',

    # Auth token required
    'like_dislike': 'main/like_dislike/{pk}/'
}
