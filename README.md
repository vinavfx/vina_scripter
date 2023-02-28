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
git clone https://github.com/fcocc77/vina_scripter.git "~/.nuke/vina_scripter"

# Windows
git clone https://github.com/fcocc77/vina_scripter.git "C:\Users\<username>\.nuke\vina_scripter"

# Or manually copy the entire git downloaded folder to the nuke user folder
```

2 - Copy this line to <b>menu.py</b>
```python
import vina_scripter
```

