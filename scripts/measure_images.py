#Finally: let's add in the ruler and template for the phenopype project

import phenopype as pp
import os

#Change and load the appropriate directory
os.chdir(r"/storage/research/iee_evol/BenSulser/2D_Morpho_Stickleback/Canad_Zoo_Training")
myproj = pp.Project(r"Canad_Zoo_Test")

#image_dir = r"/mnt/z/BenSulser/2D_Morpho_Stickleback/Canad_Zoo_Training"

#myproj.add_files(
#    image_dir=image_dir,
#    include=".JPG",      ## can be type "str" or type "list"
#    exclude=["Ruler", "test", "sudoku", "debug"],                   ## can be type "str" or type "list"
#)


#myproj.add_reference_template(
#    image_path=r"Templates/CC21L007.JPG", 
#    reference_id="scale-canad-zoo",
#    overwrite=True
#)



# Add config files to the project 
#A basic template to add to the project
template = r"/storage/research/iee_evol/BenSulser/2D_Morpho_Stickleback/Canad_Zoo_Training/Templates/pype-canad-zoo.yaml"

#Add the template the project as config files for each image
myproj.add_config(
    template_path=template, 
    tag="config-canad-zoo",  # name of the config
    overwrite=True,         # overwrite if present in image subdirectory
    interactive=False       # open the config file in an editor before saving
)

#Next: Pype on one single config - does it work/do we get a measurement? Update: it works! 
#path = myproj.dir_paths[0]

#print(path)

#pp.Pype(path, 
#        tag="config-25",         ## loads the config file "pype_config_quickestart.yaml". the tag "quickstart" gets appended to all results files
#        skip=True          ## skip=True will skip over any directories that already contain results files with "quickstart"
#        )

for path in myproj.dir_paths:
    pp.Pype(path, 
            tag="config-canad-zoo",         ## loads the config file "pype_config_quickestart.yaml". the tag "quickstart" gets appended to all results files
            skip=False,          ## skip=True will skip over any directories that already contain results files with "quickstart"
           feedback = False,
        interactive = False ## stop the GUI window for real? 
    )

#Now collect results from all images in the project, save in a new folder
myproj.collect_results(tag="config-canad-zoo", #the tag associated with the config runs          
                       files="annotations", #the type of files to collect
                       folder="measurements-canad-zoo", #the name of the new folder
                       overwrite=True)  
