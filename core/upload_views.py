from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import os
from django.conf import settings

class ImageUploadView(views.APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.data.get('file')
        if not file_obj:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save file to media folder
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
            
        file_path = os.path.join(settings.MEDIA_ROOT, file_obj.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)
        
        # Return URL
        relative_url = os.path.join(settings.MEDIA_URL, file_obj.name).replace('\\', '/')
        full_url = request.build_absolute_uri(relative_url)
        
        return Response({'url': full_url}, status=status.HTTP_201_CREATED)
