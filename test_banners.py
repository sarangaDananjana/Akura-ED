import os, sys, django
sys.path.append(r'c:\Users\Saranga\Desktop\Akura ED')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from learning.models import Banner
print("Banners in DB:", Banner.objects.count())
from learning.serializers import BannerSerializer
banners = Banner.objects.all()
data = BannerSerializer(banners, many=True).data
print(data)
