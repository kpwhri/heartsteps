import os, sys
sys.path.append('/server')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "heartsteps.settings")

from django.conf import settings
import django
django.setup()

from collections import defaultdict
from django.core import serializers                                                                     

obj_dict = defaultdict(list)
deserialized = serializers.deserialize('json', open(sys.argv[1]))
# organize by model class
for item in deserialized:
  obj = item.object
  obj_dict[obj.__class__].append(obj) 

for cls, objs in obj_dict.items():
  cls.objects.bulk_create(objs)