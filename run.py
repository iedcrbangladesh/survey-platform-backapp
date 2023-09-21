
from app import app
import os
from home import *
from cati import *
from users import *

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=True, host='0.0.0.0', port=port)
    