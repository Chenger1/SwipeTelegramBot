# Contains all the relative paths for SwipeRestApi
REL_URLS = {
    'login': 'auth/login/',
    'users': 'main/users/',
    'subscription': 'main/users/{pk}/subscription/',

    # PUBLIC
    'posts_public': 'main/posts_public/',
    'houses_public': 'main/houses_public/',
    'flats_public': 'main/flats_public/',

    # POST
    #   #COMPLAINT
    'complaint': 'main/complaints/',
    #   #FAVORITES
    'favorites': 'main/favorites_posts/',
    #   #Like/Dislike
    'like_dislike': 'main/like_dislike/{pk}/',
    #   #Filters
    'filters': 'main/user_filters/',
    #   #POSTS - user posts
    'posts': 'main/posts/',
    'promotions': 'main/promotion/',
    'promotion_types': 'main/promotion_type/',

    # HOUSES
    'houses': 'main/houses/',
    #   #FLATS
    'flats': 'main/flats/',
    'booking_flat': 'main/flats/{flat_pk}/booking/',
    'requests': 'main/requests/',
    #   #NEWS
    'news': 'main/news/',

    #   #DOCUMENTS
    'documents': 'main/documents/',
    'buildings': 'main/buildings/',
    'sections': 'main/sections/',
    'floors': 'main/floors/',
}
