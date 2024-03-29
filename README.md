# Vina Scripter
Python and Blinkscript editor for Nuke, based on the VIM editor,
inspired by <a href=https://github.com/adrianpueyo/KnobScripter target='_blank'>KnobScripter</a>, but rewritten,
the idea that is simpler and more useful and without the option to edit external files.

Showing: <a href=https://vinavfx.com/blog target='_blank'>https://vinavfx.com/blog</a>


# Feautres
- Edit <b>Temporary Scripts</b> to make it work and create ':tabnew' tabs and close them 'tabclose'
- Ability to edit any <b>Expression</b> of any knob in python or tcl
- Automatic detection of <b>Blinkscript</b>, <b>TCL</b> and <b>Python</b> knob
- It is scalable to add more shortcuts and missing <b>VIM</b> commands

# Installation
1 - Copy to nuke folder
```sh
# Linux:
cd ~/.nuke
git clone --recursive https://github.com/vinavfx/vina_scripter.git

# Windows
# Download git: https://git-scm.com/download/win
git clone --recursive https://github.com/vinavfx/vina_scripter.git "C:\Users\<username>\.nuke\vina_scripter"

# Or manually copy the entire git downloaded folder and its submodules to the nuke user folder
```

2 - Copy this line to <b>menu.py</b>
```python
import vina_scripter
vina_scripter.setup()
```

# Basic Use
To use the editor without vim mode, press the 'Vim' button on the top right, and it will work like a normal editor !
- <b>:w</b> : Save script to node
- <b>:wq</b> : Save node and Exit
- <b>:q</b> : Exit node
- <b>:tabnew</b> : New script page
- <b>:tabclose</b> : Close script page
- <b>:tabo</b> : Close all except the current page
- <b>:1, :2, :3...</b> : Go to line
- <b>/</b> : Search
- <b>:retab</b> : Change the indentation to 4 spaces

- <b>i</b> : Insert mode
- <b>v</b> : Visual mode
- <b>V</b> : Visual Line mode
- <b>Ctrl+[</b> : Exit modes and exit selected words
- <b>*</b> : Find word under cursor

- For all shortcuts and commands see them here, <a href=https://vim.rtorr.com target='_blank'>vim.rtorr.com</a>
not all vim shortcuts are implemented in <b>Vina Scripter</b> !
In this script are all available shortcuts, in case you want to change them at will.
<a href=./src/vim/keys_vim_mode.py target='_blank'>keys_vim_mode.py</a>


# Screenshots

- <b>TABS</b>

![image](screenshots/tabs.jpg)

- <b>COMMAND LINE</b> 

![image](screenshots/command_line.jpg)

- <b>NORMAL</b> Mode

![image](screenshots/normal_mode.jpg)

- <b>INSERT</b> Mode

![image](screenshots/insert_mode.jpg)

- <b>VISUAL</b> Mode

![image](screenshots/visual_mode.jpg)

- <b>VISUAL LINE</b> Mode

![image](screenshots/visual_line_mode.jpg)

- <b>BLINKSCRIPT</b> Code

![image](screenshots/blinkscript.jpg)

- <b>PYTHON</b> Code

![image](screenshots/python.jpg)

- <b>TCL</b> Multidimensional Code

![image](screenshots/tcl.jpg)
