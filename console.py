import sys
import getopt
import os
import csv

if __name__ == "__main__":
    base_path = os.path.realpath(__file__).replace(os.path.basename(__file__), '')
    input_file = None
    output_file = None
    attachments = False
    template_file = "/tests/data/template.eml"
    template_attachment_file = "/tests/data/template_attachment.eml"
    file_dir = "/tests/data/files"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["input=", "output="])
    except getopt.GetoptError:
        print("-i <INPUTFILE> and -o <OUTPUTFILE> required")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print("-i <INPUTFILE> -o <OUTPUTFILE> -a")
            sys.exit()
        elif opt in ("-i", "--input"):
            input_file = base_path + arg
            if not os.path.isfile(input_file):
                print("Input file {} is missing".format(input_file))
                sys.exit(2)
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("a", "--attachments"):
            attachments = True
        elif opt in ("f", "--files"):
            file_dir = arg

            if not os.path.isdir(file_dir):
                print("File dir {} does not exist".format(file_dir))
                sys.exit(2)
        elif opt in ("t", "template"):
            template_file = arg
            template_attachment_file = template_file.replace(".eml", "_attachment.eml")

            if not os.path.isfile(template_file) or not os.path.isfile(template_attachment_file):
                print("Template files {} and/or {} are missing".format(template_file, template_attachment_file))
                sys.exit(2)

    with open(input_file) as csv_file:
        content = csv.reader(csv_file, delimiter=',', quotechar='"')
        for row in content:
            print(row)

# ##DOCUMENTNAME##
# ##CONTENTID##
# ##BASE64##
# ##ID##