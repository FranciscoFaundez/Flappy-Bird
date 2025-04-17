import pyglet
import numpy as np
from pyglet.gl import *
from pyglet.window import key

import os

root = (os.path.dirname(__file__))

from librerias.scene_graph import *
from librerias import shapes
from librerias.drawables import Model

WIDTH = 1000
HEIGHT = 1000
GRAVITY = -1.5
JUMP = 0.75

#Controller
class Controller(pyglet.window.Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0.0
        # 0 = Inicio, 1 = En juego,  2 = Game Over
        self.gameState = 0
        # Velocidad del pájaro en el eje y
        self.bird_vel = 0
        # Posición del pájaro en el eje y
        self.bird_pos = 0

window = Controller(WIDTH, HEIGHT, "Tarea 2")


if __name__ == "__main__":
    
    vertex_source = """
#version 330

in vec3 position;
in vec2 texCoord;

uniform mat4 u_model = mat4(1.0);
uniform mat4 view = mat4(1.0);
uniform mat4 projection = mat4(1.0);

out vec2 fragTexCoord;

void main() {
    fragTexCoord = texCoord;
    gl_Position = projection * view * u_model * vec4(position, 1.0f);
}
    """
    fragment_source = """
#version 330

in vec2 fragTexCoord;

out vec4 outColor;

uniform sampler2D u_texture;

void main() {
    outColor =  texture(u_texture, fragTexCoord);
    if(outColor.a < 0.1)
        discard;
}
    """

    
    vert_program = pyglet.graphics.shader.Shader(vertex_source, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)

    #Grafo de escena
    graph = SceneGraph()


    graph.add_node("scene", 
        transform=tr.identity()
    )

    quad = Model(shapes.Square["position"], shapes.Square["uv"], index_data=shapes.Square["indices"])
    graph.add_node("bird",
                    attach_to="scene",
                    mesh=quad, 
                    pipeline=pipeline, 
                    texture=Texture(root + "/assets/bird_body.png"),
                    scale = [0.15, 0.1, 0.15],
                    cull_face=True)

    # Poner ala al pajarillo
    graph.add_node("wing",
                    attach_to="bird",
                    mesh=quad, 
                    pipeline=pipeline,
                    texture=Texture(root + "/assets/bird_wing.png"),
                    scale = [0.4, 0.4, 0],
                    position = [-0.2, 0, -0.01], # Para que el ala se vea sobre el cuerpo y en la posición correcta
                    cull_face=True
                   )

    @window.event
    def on_draw():
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 0.0)
        window.clear()

        graph.draw()


    @window.event
    def on_key_press(symbol, modifiers):
        # Si no ha perdido
        if (window.gameState != 2):
            # Si presiona espacio
            if symbol == key.SPACE: 
                window.gameState = 1
                window.bird_vel = JUMP

    def update(dt):
        # El tiempo queda guardado en la variable window.time
        window.time += dt

        # Actualizar velocidad y posición si el juego ha empezado
        if (window.gameState != 0):  
            window.bird_vel += GRAVITY * dt
            window.bird_pos += window.bird_vel * dt


        if (window.gameState == 1): 
            graph["wing"]["transform"] = (
                tr.translate(0.45, 0.0, -0.01)  # Posición final + Z adelante para que el ala se vea delante del pájaro
                @ tr.rotationZ(0.13 * np.sin(8 * window.time)) # Aleteo
                @ tr.translate(-0.5, -0.05, 0)  # Traslado para que gire en torno a la punta del ala
                )
        
        # Actualizar posición del pájaro
        graph["bird"]["transform"] = (
            tr.translate(0, window.bird_pos, 0)
        )
        


        # Si el pájaro toca el techo o suelo, pierde
        if (window.bird_pos >= 0.95 or window.bird_pos <= -0.95):
            window.gameState = 2


        graph.update()



    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()

    

    
    
