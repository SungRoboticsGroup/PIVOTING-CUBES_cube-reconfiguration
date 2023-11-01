Code from:

Daniel Feshbach and Cynthia Sung, 
"Reconfiguring Non-Convex Holes in Pivoting Modular Cube Robots," 
in IEEE Robotics and Automation Letters, vol. 6, no. 4, pp. 6701-6708, 
Oct. 2021, doi: 10.1109/LRA.2021.3095030.

Paper full text available at 
https://repository.upenn.edu/items/f99ad843-6a6e-4d69-b36e-f449550b7fbf

This code uses python to compute reconfiguration plans and output them as 
*.record files. Then it uses MATLAB to animate the plans in 3D. 

The code makes plans to turn admissible configurations into lines.
To turn it into another admissible configuration, the idea would be to then 
find the plan to turn the target configuration into a line, and reverse it.

Dependencies for python (most recently tested with 3.11):

    pygame (I installed with pip3 install pygame)
    possibly other things that come installed with spyder

Dependencies for MATLAB (most recently tested with R2023b):
Simulink 3D Animation

Working example to install, e.g in miniconda with python 3.11:
    
    conda create -name pivoting_cubes
    conda activate pivoting_cubes
    conda install -c anaconda spyder
    pip3 install pygame

To generate reconfiguration plans:

- Edit main() in Configuration.py

- Make a configuration as an object of the Configuration class. The constructor 
has the following parameters:

    - cubes - the grid locations (x,y,z) integers of the set of cubes, given
                as a list of 3-tuples or as the name of a csv file with columns
                        x, y, z, r, g, b, alpha
                        where r,g,b,alpha are for color and transparancy
      
    - dodraw - animate the reconfiguration, ONLY WORKS FOR 2D CONFIGURATIONS.
      
    - dosave - boolean indicating whether it should save the flattening plan
      
    - saveprefix - if dosave, it will save the reconfiguration plan in a file 
                    named saveprefix+"_steps.record"
      
    - tailsizelimit - defaults to None. If set to a non-negative integer, the 
                        generated flattening plans will only generate the tail up
                        to that length. This can be convenient for animating or 
                        explaining plans, to avoid most of the plan being filled 
                        up with "the current module moves one step along the tail".
    - ispar - not tested with 2021 algorithm, don't use

- Call the flatten() method on your Configuration object

Example:

    testname = 'inbranch_L_3D'
    c = Configuration(testname+'.csv', dosave=True, saveprefix=testname+"_clipped", tailsizelimit=5)
    c.flatten()

In the above example, we put "clipped" in the saveprefix to indicate that we
are using a tail size limit - this is just our file naming convenction.

You can view 3D configurations (from CSV files) in MATLAB with plotCubes.m,
running the function as, e.g., plotCubes("inbranch_L_3D.csv") and then pan 
around in 3D for the cubes to start rendering.

To animate 3D reconfiguration plans, use the makevideo.m MATLAB file. 

    makevideo(filename, savefile, speedup)
    filename - string name of .record file containing the plan
    savefile - true/false whether to save the result as an animation
    speedup - number of frames generated per frame saved


Example:

    makevideo('./inbranch_L_3D_clipped_steps.record', true, 10)
