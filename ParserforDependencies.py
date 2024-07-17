import os
import re
import sys
import webbrowser
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import write_dot

from pyvis.network import Network

class Bcolors:
    OKGREEN = '\033[92m'
    HEADER = '\033[95m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    OKBLUE = '\033[94m'
    BOLD = '\033[1m'

class Texfile():

    def __init__(self, name, parentname, parentpath, is_class):
        if ".tex" in name.lower():
            self.name = name.replace(" ","")
        else:
            self.name = add_extension(name, is_class)
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


    def has_inputs(self):
        if len(self.inputlist) == 0:
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


def add_extension(name, is_class=False):
    if is_class == True:
        return name.replace(" ","") + ".cls"
    else:
        return name.replace(" ","") + ".sty"

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

    if type(oldlist) != list:
        newlist = oldlist.split(",")
    else:
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
        found_patterns.extend(re.findall(patterns,file,re.VERBOSE))

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

def debug_print_function(main_parent, active_childlist):
    main_parent.to_string()

    print(f"Lenght of active_childlist is {len(active_childlist)}")

    for i, items in enumerate(active_childlist):
        print(f"Current iteration is {i+1}")
        items.to_string()


if __name__ == "__main__":

# Startup
    parser = argparse.ArgumentParser()

    parser.add_argument("-outfile", "--outfilename", help="Name of the outfile. Should end with .html but programm will add it.")
    parser.add_argument("-s", "--sourcefile", help="Name of the sourcefile. Has to be a .tex in current directory.")
    parser.add_argument("-b", default=True, action="store_false", help="If set the outfile will not be opened at the end. Default is true.")
    parser.add_argument("-i", default=False, action="store_true", help="If set \\include and \\input while be ignored.")
    parser.add_argument("-pipe", default=False, action="store_true", help="Uses a adjazenzlist to generate a graph in differend formats")

    args = parser.parse_args()

# Caching Errors in the console input
    if args.sourcefile == None:
        print("Missing sourcefile. Please give a sourcefile. \n"
              "\n"
              "Example: python3 ParserforDependencies.py -s example.tex \n"
              "\n"
              "For further help enter: python3 ParserforDependencies.py -h \n")
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

    packages = extract_package_infomation(file)
    tex_class = extract_class_infomation(file)

    if not tex_class:
        print("\n"
              "No documentclass was found. Make sure the source has a doumentclass. Exeting programm"
              "\n")
        sys.exit(1)

    main_parent = Texfile(args.sourcefile, None, None, False)
    main_parent.set_path(find_path(args.sourcefile, os.getcwd()))

    active_childlist = []

    if args.i is False:
            main_parent.set_inputlist(extract_input_information(file))
            for items in main_parent.inputlist:
                packages_in_inputs = extract_package_infomation(read_file(items))
                for objects in packages_in_inputs:
                    if type(objects) is tuple:
                        option, tex_class = objects
                        option = split_string_by_comma(option)
                        tex_class = split_string_by_comma(tex_class)
                        for elements in tex_class:
                            child = Texfile(elements, items, find_path(items, os.getcwd()), False)
                            child.optionlist.append(option)
                            main_parent.childlist.append(child.name)
                            active_childlist.append(child)
                    else:
                        if type(packages_in_inputs) == list:
                            child = Texfile(tex_class[0], items, find_path(items, os.getcwd()), False)
                        main_parent.childlist.append(child.name)
                        active_childlist.append(child)

    tex_class = extract_class_infomation(file)

    for items in tex_class:
        if type(items) is tuple:
            option, tex_class = items
            option = split_string_by_comma(option)
            tex_class = split_string_by_comma(tex_class)
            for elements in tex_class:
                child = Texfile(elements, main_parent.name, main_parent.path, True)
                child.optionlist.append(option)
                main_parent.childlist.append(child.name)
                active_childlist.append(child)
        else:
            if type(tex_class) == list:
                child = Texfile(tex_class[0], main_parent.name, main_parent.path, True)
            main_parent.childlist.append(child.name)
            active_childlist.append(child)

    for items in packages:
        if type(items) is tuple:
            options, package = items
            options = split_string_by_comma(options)
            package = split_string_by_comma(package)
            for elements in package:
                child = Texfile(elements, main_parent.name, main_parent.path, False)
                child.optionlist.append(options)
                main_parent.childlist.append(child.name)
                active_childlist.append(child)
        else:
            child = Texfile(items, main_parent.name, main_parent.path, False)
            main_parent.childlist.append(child.name)
            active_childlist.append(child)

    for children in active_childlist:
        print(children.name, children.path)
        file = read_file(children.path)
        packages = extract_package_infomation(file)
        inputs = extract_input_information(file)
        for items in packages:
            if type(items) is tuple:
                options, package = items
                if not os.path.splitext(children.name)[0] == package:
                    child = Texfile(package, children.name, children.path, False)
                    child.optionlist.append(options)
                    children.childlist.append(child.name)
                    active_childlist.append(child)
                else:
                    print(f"{Bcolors.FAIL}WARNING: {Bcolors.ENDC}In the package {children.name} seams to be a self reference. The found package in the file {children.name} was {items}. This package while be ignored")
            else:
                if not os.path.splitext(children.name)[0] == items:
                    child = Texfile(items, children.name, children.path, False)
                    children.childlist.append(child.name)
                    active_childlist.append(child)
                else:
                    print(f"{Bcolors.FAIL}WARNING: {Bcolors.ENDC}In the package {children.name} seams to be a self reference. The found package in the file {children.name} was {items}. This package while be ignored")


# Output on Console
    print(f"\n"
          f"All packages for {args.sourcefile} where found. A total of {len(active_childlist)} are used in this file\n"
          f"\n"
          f"Inputfile has the following packages: \n"
          f"{main_parent.childlist}"
          f"\n"
          f"Other packages requierd are: \n")
    for items in active_childlist:
        if not items.is_child_list_empty():
            if items.has_options():
                print(f"- Package {items.name} with the options {items.optionlist} requiers: {items.childlist}")
            else:
                print(f"- Package {items.name} requiers: {items.childlist}")

    if args.i == False:
        if main_parent.has_inputs():
            print(f"\n"
                  f"Inputs in {main_parent.name} are:\n"
                  f"{main_parent.inputlist}")

    debug_print_function(main_parent, active_childlist)

# Graph

    net = Network(width="100%", height=1000, directed=True, select_menu=True, filter_menu=True)
    net.add_node(main_parent.name, label=main_parent.name, color="#00ff1e", shape="circle")

    if args.i == False:
        if main_parent.has_inputs():
            for items in main_parent.inputlist:
                net.add_node(items, label=items, color="#ff001e", shape="circle")
                net.add_edge(main_parent.name, items)

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

    if args.pipe == True:
        adjenzlist = net.get_adj_list()

        # Dot
        Graph = nx.DiGraph(adjenzlist)
        write_dot(Graph, "graph.dot")
        print("A DOT file was created containg the graph")

    print("Program finished without errors \n")