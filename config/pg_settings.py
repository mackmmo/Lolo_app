from .settings import *

import os

import dj_database_url
# Make OSGeo4W DLLs discoverable (GeoDjango / PostGIS)

if sys.platform == "win32":
    os.environ["PATH"] = r"C:\Users\basel\AppData\Local\Programs\OSGeo4W\bin;" + os.environ.get("PATH", "")
    GDAL_LIBRARY_PATH = r"C:\Users\basel\AppData\Local\Programs\OSGeo4W\bin\gdal312.dll"
    GEOS_LIBRARY_PATH = r"C:\Users\basel\AppData\Local\Programs\OSGeo4W\bin\geos_c.dll"

# Default local DB (works without env vars)
import os
import dj_database_url

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
