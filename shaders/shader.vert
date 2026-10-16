#version 400 core
/*
 Vertex shader: passes vertex position and per-vertex color directly without transformation.
*/

layout(location = 0) in vec4 v_position;
layout(location = 1) in vec4 v_color;

out vec4 v2f_color;

void main() {
    gl_Position = v_position;
    v2f_color = v_color;
}