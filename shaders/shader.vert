#version 400 core

layout(location = 0) in vec4 v_position;
layout(location = 1) in vec4 v_color;

uniform vec2 u_offset;
uniform float u_scale;
uniform float u_angle;
uniform vec4 u_color;
uniform vec2 u_proj;

out vec4 v2f_color;

void main() {
    float c = cos(u_angle);
    float s = sin(u_angle);
    mat2 rot = mat2(c, s, -s, c);
    vec2 pos = (rot * (v_position.xy * u_scale)) + u_offset;
    gl_Position = vec4(pos * u_proj, 0.0, 1.0);
    v2f_color = v_color * u_color;
}
