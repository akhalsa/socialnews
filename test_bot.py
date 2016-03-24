import facebook

graph = facebook.GraphAPI(access_token='CAACzgeJoVHgBALjMQAMclitrIPMvdlZBVUtvTLkCaJeqOC2kwRJugqQNRsl0vZBSiizNrhSkEq15tHWZAfBKmYJ9xOcj4FurKnp2A3XP3k5SulX8j5HqBQ3Bl6hf2ZAWz07xbni3ZBQ8KyChlXJThocFXNiR5wSGVNIyNd4nfhlvtidZBmjeZAQ', version='2.5')


attachment =  {
    'name': 'Link name',
    'link': 'http://www.example.com/',
    'caption': 'Check out this example',
    'description': 'This is a longer description of the attachment',
    'picture': 'http://www.example.com/thumbnail.jpg'
}

graph.put_wall_post(message='Check this out...', attachment=attachment, profile_id='1578415282450261')