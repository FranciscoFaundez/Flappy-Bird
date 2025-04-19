import pyglet
import numpy as np
import random
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
        # Posición del nodo 1 y 2 del background
        self.back1= 0
        self.back2 = 0

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
    
    graph.add_node("background1",
                   attach_to="scene",
                   mesh=quad,
                   pipeline=pipeline,
                   texture=Texture(root + "/assets/back.jpg"),
                   scale = [2, 2, 0]

    )

    graph.add_node("background2",
                attach_to="scene",
                mesh=quad,
                pipeline=pipeline,
                texture=Texture(root + "/assets/back.jpg"),
                scale = [2, 2, 0]
    )


    # Almacenaremos las tuberías que crearemos en una lista
    pipes = []
    pipe_timer = 0
    pipe_interval = 2.5  # segundos
    pipe_speed = 0.8

    # Función para crear el nodo superior e inferior de las tuberías que iremos usando
    def create_pipe():

        # Asignamos una id a cada tubería
        pipe_id = f"pipe_{len(pipes)}"

        print(pipe_id)

        # Espacio aleatorio entre la tubería superior e inferior
        gap_size = random.uniform(0.3, 1.0)

        # Rango permitido para el centro del gap
        min_center = -0.6 + gap_size / 2
        max_center = 0.6 - gap_size / 2

        gap_center = random.uniform(min_center, max_center)


        # Posición de las tuberías (centro)
        top_pipe_y = gap_center + gap_size / 2 + 1  # su centro está 1 unidad arriba de su extremo inferior
        bottom_pipe_y = gap_center - gap_size / 2 - 1  # su centro está 1 unidad abajo de su extremo superior



        # Desplazamientos desde el centro original (0)
        top_displacement = top_pipe_y
        bottom_displacement = bottom_pipe_y

        # Habrá un nodo padre que contenga a la tubería superior e inferior
        graph.add_node(pipe_id, attach_to="scene", transform=tr.identity())

        # Inferior
        graph.add_node(f"{pipe_id}_bot",
            attach_to=pipe_id,
            mesh=quad,
            pipeline=pipeline,
            texture=Texture(root + "/assets/pipe.png"),
            position=[1.2, bottom_displacement, -0.2],
            scale=[0.22, 2, 1],
            rotation=[0, 0, np.pi]  # rotado para que mire hacia arriba

        )

        # Superior
        graph.add_node(f"{pipe_id}_top",
            attach_to=pipe_id,
            mesh=quad,
            pipeline=pipeline,
            texture=Texture(root + "/assets/pipe.png"),
            position=[1.2, top_displacement, -0.1],
            scale=[0.22, 2, 1]
        )

        pipes.append({"id": pipe_id, "x": 1})

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
        global pipe_timer
        # El tiempo queda guardado en la variable window.time
        window.time += dt
        # Tiempo para que salga una nueva tubería
        pipe_timer += dt
        # Solo generar si está jugando
        if window.gameState == 1 and pipe_timer >= pipe_interval:
            create_pipe()
            pipe_timer = 0


        # Actualizar velocidad y posición si el juego ha empezado
        if (window.gameState != 0):  
            window.bird_vel += GRAVITY * dt
            window.bird_pos += window.bird_vel * dt

        # Movimiento del ala
        if (window.gameState == 1): 
            graph["wing"]["transform"] = (
                tr.translate(0.45, 0.0, -0.01)  # Posición final + Z adelante para que el ala se vea delante del pájaro
                @ tr.rotationZ(0.13 * np.sin(8 * window.time)) # Aleteo
                @ tr.translate(-0.5, -0.05, 0)  # Traslado para que gire en torno a la punta del ala
                )

            # Movimiento del fondo
            speed = 0.2 * dt
            window.back1 -= speed
            window.back2 -= speed


            # Si alguno se va fuera, lo reposicionamos al otro lado
            if window.back1 <= -2.0:
                window.back1 += 4.0

            if window.back2 <= -4.0:
                window.back2 += 4.0

            # Aplicar transformación
            graph["background1"]["transform"] = tr.translate(window.back1, 0, 0)
            graph["background2"]["transform"] = tr.translate(window.back2 + 2, 0, 0)
            
        # Actualizar posición del pájaro
        graph["bird"]["transform"] = (
            tr.translate(0, window.bird_pos, 0)
        )
    

        # Si el pájaro toca el techo o suelo, pierde
        if (window.bird_pos >= 0.95 or window.bird_pos <= -0.95):
            window.gameState = 2


        graph.update()

        if window.gameState == 1:
            # Movemos las tuberías
            #print(pipes)
            for pipe in pipes:
                #print(pipe)
                pipe["x"] -= pipe_speed * dt
                graph[pipe["id"]]["transform"] = tr.translate(pipe["x"], 0, -0.1)


            """
            # Eliminamos las tuberías fuera de pantalla
            print("pipes: " + str(pipes[:]))
            for pipe in pipes[:]:
                print(pipe)
                if pipe["x"] < -4:
                    
                    graph.remove_node(pipe["id"])
                    pipes.remove(pipe)

            """


    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
