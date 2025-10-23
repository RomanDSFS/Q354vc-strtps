#import os

#UPLOAD_DIR = "uploads/"
#os.makedirs(UPLOAD_DIR, exist_ok=True)
import os

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
