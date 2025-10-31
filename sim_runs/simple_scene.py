import genesis as gs

from src.utils.debug import enter_interactive

gs.init(backend=gs.gpu)
scene = gs.Scene(show_viewer=True, show_FPS=False)
scene.add_entity(gs.morphs.Plane())

obj = scene.add_entity(
    gs.morphs.MJCF(
        file="/workspace/RoboSandbox/assets/CHICKEN_RACER/model.xml",
        pos=[0,0,0],
        quat=[1,0,0,0],
        visualization=True,
        collision=True,
        convexify=False,
    ),
    material=gs.materials.Rigid(),
    surface=gs.surfaces.Default(vis_mode="collision"),
)

def steps(n=1):
    for _ in range(n):
        scene.step()

scene.build()

scene.step()
enter_interactive()

while True:
    scene.step()

