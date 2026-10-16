#version 400 core
/*
 Fragment shader: outputs the interpolated vertex color directly to the framebuffer.
*/

in vec4 v2f_color;
out vec4 frag_color;

void main() {
    frag_color = v2f_color;
}
