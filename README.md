# MTs3DGrapher

A simple 3D graphing program to teach kids about the coordinates system

About:

My kid came home with homework to plot points on a 3D coordinates system. They were doing it by hand. There had to be a better way so we built this program to do it. 
You write out the sets of points you want (lines) in a JSON file and the program plots them out. Easy peasy and its lots of fun. 

Installation: 

Only tested on a Mac. 

Requirements:

1) Python 2.7
2) Xcode command line tools (install from app store)
3) pygame: sudo pip install pygame
4) Python OpenGL: pip install PyOpenGL PyOpenGL_accelerate

Use:
python shapes.pl [JSON_FILE]
JSON file will default to shapes.json in the same dir

Click on the mouse to rotate the coordinates 
Arrow keys move up/down and left/right
+ and - keys zoom in and out
“r” key resets view
“t” key toggles ticks on the axis 
“n” key shows names of each shape

Edit the shapes.json file and see your shapes update in the coordinates system. 
Each shape is a series of lines composed of 2 points. 

Enjoy


