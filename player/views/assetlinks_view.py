import os
from django.http import HttpResponse
from wild_politics.settings import BASE_DIR

def assetlinks_view(request):
    file_path = os.path.join(BASE_DIR, '.well-known', 'assetlinks.json')
    with open(file_path, 'r') as file:
        data = file.read()
    return HttpResponse(data, content_type='application/json')
