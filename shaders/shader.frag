#version 400 core

in vec4 v2f_color;

uniform float u_attenuation;

out vec4 frag_color;

void main() {
    frag_color = vec4(v2f_color.rgb * u_attenuation, v2f_color.a);
}
