#Let's add in the ruler and template for the phenopype project

import phenopype as pp
import os
import argparse


def main(base_dir, pheno_name, image_dir, template_path, template_id):
    #Change and load the appropriate directory - please refer to the phenopype documentation for more details on how to set up a project https://phenopype.readthedocs.io/en/latest/quickstart.html#creating-a-project
    os.chdir(base_dir)
    myproj = pp.Project(pheno_name)


    myproj.add_files(
        image_dir=image_dir,
        exclude=["Ruler", "test", "debug"],                   ## can be type "str" or type "list"
    )

    myproj.add_reference_template(
        image_path=template_path,
        reference_id=template_id,
        mode = "link",
        overwrite=True
    )

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize phenopype project with reference template.")
    parser.add_argument("--base_dir", type=str, required=True, help="Base directory for the phenopype project.")
    parser.add_argument("--pheno_name", type=str, required=True, help="Name of the phenopype project.")
    parser.add_argument("--image_dir", type=str, required=True, help="Directory containing the images to be added to the project.")
    parser.add_argument("--template_path", type=str, required=True, help="Path to the reference template image.")
    parser.add_argument("--template_id", type=str, required=True, help="Identifier for the reference template. Cannot use underscores")

    args = parser.parse_args()
    main(args.base_dir, args.pheno_name, args.image_dir, args.template_path, args.template_id)