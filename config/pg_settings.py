from .settings import *

import dj_database_url
import os
import sys

if sys.platform == "win32":
    os.environ["PATH"] = r"C:\Users\basel\AppData\Local\Programs\OSGeo4W\bin;" + os.environ.get("PATH", "")
    os.environ["GDAL_LIBRARY_PATH"] = r"C:\Users\basel\AppData\Local\Programs\OSGeo4W\bin\gdal312.dll"
    os.environ["GEOS_LIBRARY_PATH"] = r"C:\Users\basel\AppData\Local\Programs\OSGeo4W\bin\geos_c.dll"
else:
    # make sure we DON'T carry Windows values in production
    os.environ.pop("GDAL_LIBRARY_PATH", None)
    os.environ.pop("GEOS_LIBRARY_PATH", None)

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

# If DATABASE_URL is set, use it (Render / remote)
if os.environ.get("DATABASE_URL"):
    DATABASES["default"] = dj_database_url.parse(
        os.environ["DATABASE_URL"],
        conn_max_age=600,
        ssl_require=True,
    )
