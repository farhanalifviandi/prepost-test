import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel needs the app to be callable as handler
def handler(request, context):
    return app(request.environ, context)

# For Vercel Python runtime
app = app