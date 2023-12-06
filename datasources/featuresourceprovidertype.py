from enum import Enum, auto


class FeatureSourceProviderType(str, Enum):
    Unknown = auto()
    # KingOracle = "KING.ORACLE"
    # AutodeskOracle = "AUTODESK.ORACLE"
    # AutodeskTopobase = "AUTODESK.TOPOBASE"
    # Shape = "OSGEO.SHP"
    # Sdf3 = "OSGEO.SDF"
    # OSGeoWms = "OSGEO.WMS"
    # OSGeoWfs = "OSGEO.WFS"
    # OSGeoGdal = "OSGEO.GDAL"
    Sqlite = "OSGEO.SQLITE"
    PostgreSQL = "OSGEO.POSTGRESQL"
    # MySql = "OSGEO.MYSQL"
    # SQLServerSpatial = "OSGEO.SQLSERVERSPATIAL"
    # OSGeoOgr = "OSGEO.OGR"
