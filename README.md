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


# Screenshots

- <b>NORMAL</b> Mode

![Alt text](screenshots/normal_mode.jpg?raw=true "Optional Title")

- <b>INSERT</b> Mode

![Alt text](screenshots/insert_mode.jpg?raw=true "Optional Title")

- <b>VISUAL</b> Mode

![Alt text](screenshots/visual_mode.jpg?raw=true "Optional Title")

- <b>VISUAL LINE</b> Mode

![Alt text](screenshots/visual_line_mode.jpg?raw=true "Optional Title")

- <b>COMMAND LINE</b> 

![Alt text](screenshots/command_line.jpg?raw=true "Optional Title")

- <b>BLINKSCRIPT</b> Code

![Alt text](screenshots/blinkscript.jpg?raw=true "Optional Title")

- <b>PYTHON</b> Code

![Alt text](screenshots/python.jpg?raw=true "Optional Title")
