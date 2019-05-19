# 前言
 Pyqt5的动手实践，主要调用了nilearn库的函数对CT图像文件进行了处理。下面的选项均出自nilearn的官方文档。  
 
 # User guide:
* Step 1: Click 'File' on the menuBar, choose '*.nii' file to open.
* Step 2: Use Sliders or Cursors to change slices.
* Step 3: Click 'Slice' on the menuBar, save '*.png' files.

# Cursors:
* When cursors are on the scene, you can use cursor to switch other two scenes which depends on the chosen coordinates.

# Sliders&Slice:
* ‘x’ is sagittal, ‘y’ is coronal, ‘z’ is axial
* Drag Sliders under scenes to change slices, the range of sliders depends on the affine of the opened file.

# Threshold:
* a number, None
* If None is given, the image is not thresholded. If a number is given, it is used to threshold the image: values below the threshold (in absolute value) are plotted as transparent. If auto is given, the threshold is determined magically by analysis of the image.

# Colors:
* Change Colors should be used after opening a file.
* Commands which take color arguments can use several formats to specify the colors. For the basic built-in colors, you can use a single letter
	- b: blue
	- g: green
	- r: red
	- c: cyan
	- m: magenta
	- y: yellow
	- k: black
	- w: white
* To use the colors that are part of the active color cycle in the current style, use C followed by a digit. For example:
	- C0: The first color in the cycle
	- C1: The second color in the cycle
* Gray shades can be given as a string encoding a float in the 0-1 range, e.g.:
	- color = '0.75'
* For a greater range of colors, you have two options. You can specify the color using an html hex string, as in:
	- color = '#eeefff'
	- Don't forget the symbol '#'
* (possibly specifying an alpha value as well), or you can pass an (r, g, b) or (r, g, b, a) tuple, where each of r, g, b and a are in the range [0,1].
* Finally, legal html names for colors, like ‘red’, ‘burlywood’ and ‘chartreuse’ are supported.
	- You may find these colors in hexadecimal colour code.

# black_bg
* True or False
If True, the background of the image is set to be black. 

# Filled
* True or False
* contours with color fillings use argument filled=True

# Annotate
* True or False
* If annotate is True, positions and left/right annotation are added to the plot.

# Interactive html viewer
* 2D based images
* It gives more interactive visualizations in a web browser.
* Interactive html viewer of a statistical map, with optional background.

# Surface html viewer
* 3D based images
* Insert a surface plot of a statistical map into an HTML page.
