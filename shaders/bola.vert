#version 400 core
/*
 Vertex shader: translates and scales a 2D geometry using uniforms,
 passing the per-vertex color attribute to the fragment shader.
*/

layout(location = 0) in vec4 v_position;
layout(location = 1) in vec4 v_color;

uniform vec2 u_offset;
uniform float u_scale;

out vec4 v2f_color;

void main() {
    gl_Position = vec4(v_position.xy * u_scale + u_offset, v_position.zw);
    v2f_color = v_color;
}