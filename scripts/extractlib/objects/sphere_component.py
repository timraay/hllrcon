from scripts.extractlib.loader import Model, Object
from scripts.extractlib.structs.vec3 import Vec3


class SphereComponentProperties(Model):
    sphere_radius: float
    relative_location: Vec3 = Vec3(x=0, y=0, z=0)


class SphereComponent(Object[SphereComponentProperties]):
    pass
