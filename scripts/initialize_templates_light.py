# setup_template.py  (run manually: python setup_template.py)
import phenopype as pp
import cv2
import argparse


def main(template_name, ref_image_path):
    # Open your reference image interactively
    ref_image = pp.load_image(ref_image_path)

    template_path = f"data/templates/template_{template_name}.png"

    template = pp.preprocessing.create_reference(
        ref_image, mask=True,
        template_id=template_name
        # ... user draws ROI interactively here
    )

    coords = template['reference'][template_name]['data']['mask'][0]

    ## save template image
    box = ref_image[coords[0][1]:coords[2][1], coords[0][0]:coords[1][0]]
    cv2.imwrite(template_path, box)
    print(f"Saved file: {template_path}")

    pp.core.export.save_annotation(template, dir_path="data/templates/")  # Save the template for later use 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set up phenopype template.")
    parser.add_argument("--template_name", type=str, required=True, help="Identifier for the reference template. Cannot use underscores.")
    parser.add_argument("--ref_image_path", type=str, required=True, help="Path to the reference image.")

    args = parser.parse_args()
    main(args.template_name, args.ref_image_path)
