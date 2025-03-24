import sys
import os

# Agregar el directorio del proyecto al PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app as application

if __name__ == '__main__':
    app.run()
