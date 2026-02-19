from .settings import *

import dj_database_url
import os
import sys


# If DATABASE_URL is set, use it (Render / remote)
if os.environ.get("DATABASE_URL"):
    DATABASES["default"] = dj_database_url.parse(
        os.environ["DATABASE_URL"],
        conn_max_age=600,
        ssl_require=True,
    )
