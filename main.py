import sys
import glfw
import moderngl
import physics
import numpy as np
from pathlib import Path

glfw.init()
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR,4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR,4)
glfw.window_hint(glfw.OPENGL_PROFILE,glfw.OPENGL_CORE_PROFILE)


janela = glfw.create_window(600,600,"Janela e contexto OpenGL",None, None)
if not janela:
    glfw.terminate()
    sys.exit("Nao abriu a janela")



glfw.make_context_current(janela)
glfw.swap_interval(1)
ctx = moderngl.create_context()

SHADERS = Path(__file__).parent / "shaders"

prog = ctx.program(vertex_shader=(SHADERS / "bola.vert").read_text(encoding="utf-8"),
                   fragment_shader=(SHADERS / "shader.frag").read_text(encoding="utf-8"),)



vertices = np.array([
     -0.5, 0.5,  0.0, 1.0,   1.0, 0.0, 0.0, 1.0,
    -0.5, -0.5, 0.0, 1.0,    1.0, 0.0, 0.0, 1.0,
    0.5, -0.5, 0.0, 1.0,     1.0, 0.0, 0.0, 1.0,
    0.5, 0.5, 0.0 ,1.0,      1.0, 0.0, 0.0, 1.0,
],dtype='f4')

indices = np.array([0,1,2,3,2,0],dtype='u4')


vbo_vertex = ctx.buffer(vertices.tobytes())
ebo = ctx.buffer(indices.tobytes())

vao = ctx.vertex_array(prog, [(vbo_vertex, '4f 4f', 'vPosition','vColors')],index_buffer=ebo)


def keyp(window,key,scancode,action,mods):
    if action != glfw.PRESS:
        return
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(janela,True)


glfw.set_key_callback(janela,keyp)


velocidade = 0.5
partida,chegada = -0.9,0.9

y_vertex = partida
t0 = glfw.get_time()
quadros,marco = 0,t0


while not glfw.window_should_close(janela):
    t1 = glfw.get_time()
    dt = t1 - t0
    t0=t1

    y_vertex += velocidade * dt

    if y_vertex > chegada:
        y_vertex = partida
    
    ctx.clear(1,1,1,1)
    prog['u_deslocamento'].value = (0,y_vertex)
    prog['u_escala'].value = 0.1
    vao.render(moderngl.TRIANGLES)

    glfw.swap_buffers(janela)
    glfw.poll_events()


ebo.release()
vao.release()
vbo_vertex.release()
prog.release()
glfw.terminate()


