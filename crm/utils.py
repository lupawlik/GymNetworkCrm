def custom_context(request):
    return {
        'user': request.user
    }
