# Cloning Machine Overhaul
Cloning Machine Overhaul is a Sims 4 mod that adds more depth and player choice to the Cloning Machine in the scientist career introduced in The Sims 4: Get To Work.

## Features

- 4 cloning options
  * Age: Create clones at any life stage. Starting from Child all the way up to Elder.
  * Sex: Pick between a masculine or a feminine body.
  * Gender: Pick between a female or male gender.
  * Family Tie: Select whether clones are regarded as offsprings or siblings of their creator.

- DNA cloning

    The cloning machine has been enhanced to allow the use of DNA samples to create clones with. Acquire the DNA of unsuspecting sims and clone them.
    
## Usage

There are two main components that have to be packaged from source in order for this mod to be functional.

- Package
  - The package file is already pre-packaged within the [assets](assets) folder for ease of use, it can be inserted directly into the game's mods folder with no hassle.
  - alternatively, the xml tunings are also contained within the [assets](assets) folder and can be used with [S4S](https://sims4studio.com/board/6/download-sims-studio-open-version) or [S4PE](https://github.com/s4ptacle/Sims4Tools/releases/) to build an entirely new package file.
    - Note that [S4S](https://sims4studio.com/board/6/download-sims-studio-open-version) and [S4PE](https://github.com/s4ptacle/Sims4Tools/releases/) are standalone programs and not supplied within this project.

- python
  - To compile the Python source into a ts4script archive, first, the required paths must be configured within [settings.py](settings.py) 
  - Following this, executing [compile.py](compile.py) will compile any .py files located in the [src](src) folder, store them within a ts4script archive and add it to the build folder within the project.
  - Additionally, [compile.py](compile.py) will attempt to copy the file into the mods folder.
