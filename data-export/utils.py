import os, sys, code

EXPORT_DIR    = os.environ["EXPORT_DIR"] 
HS_SERVER_DIR = os.environ["HS_SERVER_DIR"] 
DEBUG         = False

print(f"Configuration - EXPORT_DIR: {EXPORT_DIR}")
print(f"Configuration - HS_SERVER_DIR: {EXPORT_DIR}")

sys.path.append(HS_SERVER_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "heartsteps.settings")

from django.conf import settings
import django
django.setup()
