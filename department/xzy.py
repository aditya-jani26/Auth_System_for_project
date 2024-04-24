# def generate_token(request):
#     # Extract username and password from the request
#     username = request.data.get('username')
#     password = request.data.get('password')

#     # Authenticate the user
#     user = authenticate(username=username, password=password)
#     if user is not None:
#         # User is authenticated, generate a new token
#         token, _ = Token.objects.get_or_create(user=user)
#         return Response({'token': token.key}, status=status.HTTP_200_OK)
#     else:
#         # Authentication failed
#         return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)