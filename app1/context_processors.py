def auth_context(request):
    """
    Context processor to add authentication status to all templates
    """
    return {
        'logged_in': 'login' in request.session
    }
