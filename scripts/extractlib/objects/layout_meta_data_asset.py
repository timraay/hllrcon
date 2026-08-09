from scripts.extractlib.loader import AssetReference, Model, Object
from scripts.extractlib.structs.map_orientation import EMapOrientation
from scripts.extractlib.structs.vec2 import Vec2


class LayoutMetaDataAssetProperties(Model):
    sector_width: float
    sector_height: float
    map_width: float
    map_height: float
    map_centre: Vec2 = Vec2(x=0, y=0)
    allies_orientation: EMapOrientation
    overview_image: AssetReference | None = None


class LayoutMetaDataAsset(Object[LayoutMetaDataAssetProperties]):
    pass
