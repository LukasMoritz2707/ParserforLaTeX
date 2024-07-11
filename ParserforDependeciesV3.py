import os
import re
import sys
import webbrowser
import argparse

from pyvis.network import Network

class Texfile():

    def __init__(self, name, parentname, parentpath):
        self.name = name
        self.path = find_path(self.name, "/usr/share/texlive/texmf-dist/tex/")
        self.parent = parentname
        self.parentpath = parentpath
        self.childlist = []
        self.optionlist = []
        self.inputlist = []

    def set_path(self, path):
        self.path = path

    def set_inputlist(self, liste):
        for items in liste:
            self.inputlist.append(items)

    def to_string(self):
        print(f"Name: {self.name} \n"
              f"Path: {self.path} \n"
              f"Parent: {self.parent} \n"
              f"Parentpath: {self.parentpath} \n"
              f"Children: {self.childlist} \n"
              f"Options: {self.optionlist} \n"
              f"Inputs: {self.inputlist} \n")

    def is_child_list_empty(self):
        if len(self.childlist) == 0:
            return True
        else:
            return False

    def has_options(self):
        if len(self.optionlist) == 0:
            return False
        else:
            return True


def read_file(file):
    return open(file, "r").read()

def find_path(packagename, path):
    for root, dirs, files in os.walk(path):
        if packagename in files:
            return os.path.join(root, packagename)

def flatten(xss):
    return [x for xs in xss for x in xs]

def regex_package_pattern():
    pattern_with_options = [r"\\usepackage\s*\[(.*?)\]\s*\{\s*(.*?)\s*\}",
               r"\\RequirePackage\s*\[(.*?)\]\s*\{\s*(.*?)\s*\}",
               r"\\RequirePackageWithOptions\s*\[(.*?)\]\s*\{\s*(.*?)\s*\}"]

    pattern_without_options = [r"\\usepackage\s*\{\s*(.*?)\s*\}",
               r"\\RequirePackage\s*\{\s*(.*?)\s*\}",
               r"\\RequirePackageWithOptions\s*\{\s*(.*?)\s*\}"]

    return pattern_without_options + pattern_with_options

def regex_class_pattern():
    pattern_documentclass = [r"\\documentclass\s*\[(.*?)\]\s*\{\s*(.*?)\s*\}",
                             r"\\documentclass\s*\{\s*(.*?)\s*\}"]

    return pattern_documentclass

def regex_input_pattern():
    pattern = [r"\\input\s*\{\s*(.*?)\s*\}",
               r"\\include\s*\{\s*(.*?)\s*\}"]

    return pattern

def split_string_by_comma(oldlist):
    newlist = []

    for items in oldlist:
        if "," in items:
            parts = items.split(",")
            newlist.extend(parts)
        else:
            newlist.append(items)

    return newlist


def extract_package_infomation(file):
    pattern = regex_package_pattern()

    found_patterns = []
    for patterns in pattern:
        found_patterns.extend(re.findall(patterns,file))


    return split_string_by_comma(found_patterns)


def extract_class_infomation(file):
    pattern = regex_class_pattern()

    found_patterns = []
    for patterns in pattern:
        found_patterns.extend(re.findall(patterns,file))

    return found_patterns


def extract_input_information(file):
    pattern = regex_input_pattern()

    found_patterns = []
    for patterns in pattern:
        found_patterns.extend(re.findall(patterns, file))

    for i, items in enumerate(found_patterns):
        if not os.path.splitext(items)[1]:
            found_patterns[i] = items + ".tex"

    return found_patterns


def find_outfile_name(console_argument):
    if console_argument != None:
        if not console_argument.endswith(".html"):
            return console_argument + ".html"
        else:
            return console_argument
    else:
        return "graph.html"

def find_path(packagename, path):
    for root, dirs, files in os.walk(path):
        if packagename in files:
            return os.path.join(root, packagename)


if __name__ == "__main__":

# Startup
    parser = argparse.ArgumentParser()

    parser.add_argument("-outfile", "--outfilename", help="Name of the outfile. Should end with .html but programm will add it.")
    parser.add_argument("-s", "--sourcefile", help="Name of the sourcefile. Has to be a .tex in current directory.")
    parser.add_argument("-b", default=True, action="store_false", help="If set the outfile will not be opened at the end. Default is true.")

    args = parser.parse_args()

# Caching Errors in the console input
    if args.sourcefile == None:
        print("Missing sourcefile. Please give a sourcefile. \n"
              "\n"
              "Example: python3 main.py -s example.tex \n"
              "\n"
              "For further help enter: python3 ParserforDependenciesV2.py -h \n")
        sys.exit(1)

    if not args.sourcefile.endswith(".tex"):
        print("Sourcefile is not an .tex file. \n"
              "\n"
              "Please try again"
              "\n")
        sys.exit(1)

# Outfile build
    outfilename = find_outfile_name(args.outfilename)

# Building the main parent
    file = read_file(args.sourcefile)

    packages = extract_package_infomation(file) + extract_class_infomation(file)

    main_parent = Texfile(args.sourcefile, None, None)
    main_parent.set_path(find_path(args.sourcefile, os.getcwd()))

    main_parent.set_inputlist(extract_input_information(file))

    active_childlist = []

    for items in packages:
        if type(items) is tuple:
            options, packages = items
            child = Texfile(packages + ".sty", main_parent.name, main_parent.path)
            child.optionlist.append(options)
            main_parent.childlist.append(child.name)
            active_childlist.append(child)
        else:
            child = Texfile(items + ".sty", main_parent.name, main_parent.path)
            main_parent.childlist.append(child.name)
            active_childlist.append(child)

    for children in active_childlist:
        file = read_file(children.path)
        packages = extract_package_infomation(file)
        inputs = extract_input_information(file)
        for items in packages:
            if type(items) is tuple:
                options, package = items
                child = Texfile(package + ".sty", children.name, children.path)
                child.optionlist.append(options)
                children.childlist.append(child.name)
                active_childlist.append(child)
            else:
                child = Texfile(items + ".sty", children.name, children.path)
                children.childlist.append(child.name)
                active_childlist.append(child)

    #print(f"Lenght of active_childlist is {len(active_childlist)}")

    #for i, items in enumerate(active_childlist):
    #    print(f"Current iteration is {i+1}")
    #    items.to_string()


## Graph

    net = Network(width="100%", height=1000, directed=True, select_menu=True, filter_menu=True)
    net.add_node(main_parent.name, label=main_parent.name, color="#00ff1e", shape="circle")

    for items in active_childlist:
        net.add_node(items.name, label=items.name, shape="circle")
        if items.has_options():
            net.add_edge(items.parent, items.name, label=str(items.optionlist))
        else:
            net.add_edge(items.parent, items.name)

    net.inherit_edge_colors(False)
    net.force_atlas_2based(overlap=1)

    net.toggle_physics(False)
    net.save_graph(outfilename)

    print(f"\n"  
          f"Outputfile with Graph has been generated. Filename is {outfilename} \n")

    if args.b == True:
        url = find_path(outfilename, ".")
        webbrowser.open(url, new=2)
        print("The graph was opened in your browser \n")

    print("Program finished without errors \n")
