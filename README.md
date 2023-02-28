# Vina Scripter
Python and Blinkscript editor for Nuke, based on the VIM editor,
inspired by https://github.com/adrianpueyo/KnobScripter, but rewritten,
the idea that is simpler and more useful and without the option to edit external files,
and just it will support Nuke with Python 3, not to dirty the code,
to make it compatible with older nukes, do a Fork.


# Feautres
- Edit <b>Temporary Scripts</b> to make it work and create ':tabnew' tabs and close them 'tabclose'
- Ability to edit any <b>Expression</b> of any knob in python
- Automatic detection of the <b>Blinkscript</b> knob
- It is scalable to add more shortcuts and missing <b>VIM</b> commands

# Installation
1 - Copy to nuke folder
```sh
# Linux:
git clone --recursive https://github.com/fcocc77/vina_scripter.git "~/.nuke/vina_scripter"

# Windows
git clone --recursive https://github.com/fcocc77/vina_scripter.git "C:\Users\<username>\.nuke\vina_scripter"

# Or manually copy the entire git downloaded folder and its submodules to the nuke user folder
```

2 - Copy this line to <b>menu.py</b>
```python
import vina_scripter
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

- For all shortcuts and commands see them here, https://vim.rtorr.com/
not all vim shortcuts are implemented in <b>Vina Scripter</b> !
In this script are all available shortcuts, in case you want to change them at will.
[keys_vim_mode.py](./src/vim/keys_vim_mode.py)


# Screenshots

- <b>TABS</b>

![Alt text](screenshots/tabs.jpg?raw=true "Optional Title")


- <b>COMMAND LINE</b> 

![Alt text](screenshots/command_line.jpg?raw=true "Optional Title")

- <b>NORMAL</b> Mode

![Alt text](screenshots/normal_mode.jpg?raw=true "Optional Title")

- <b>INSERT</b> Mode

![Alt text](screenshots/insert_mode.jpg?raw=true "Optional Title")

- <b>VISUAL</b> Mode

![Alt text](screenshots/visual_mode.jpg?raw=true "Optional Title")

- <b>VISUAL LINE</b> Mode

![Alt text](screenshots/visual_line_mode.jpg?raw=true "Optional Title")

- <b>BLINKSCRIPT</b> Code

![Alt text](screenshots/blinkscript.jpg?raw=true "Optional Title")

- <b>PYTHON</b> Code

![Alt text](screenshots/python.jpg?raw=true "Optional Title")
