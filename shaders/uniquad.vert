#version 400 core
/*
 Vertex shader: scales vertex position and applies a flat uniform color.
*/

layout(location = 0) in vec4 v_position;

uniform float u_scale;
uniform vec4 u_color;

out vec4 v2f_color;

void main() {
    gl_Position = vec4(v_position.xy * u_scale, v_position.zw);
    v2f_color = u_color;
}