import os
import re
import sys
import webbrowser
import argparse

from pyvis.network import Network

class Package:

    # Variables of the class Package:
    # packagename, packagepath, father, fatherpath, childlist, optionlist

    def __init__(self, packagename, parent, parentpath):
        self.packagename = packagename
        self.packagepath = find_path(self.packagename, "/usr/share/texlive/texmf-dist/tex")
        self.parent = parent
        self.parentpath = parentpath
        self.childlist = []
        self.optionlist = []

    # to_string function
    def to_string(self):
        print(f"Package: {self.packagename} \n"
              f"Packagepath: {self.packagepath} \n"
              f"Parent: {self.parent} \n"
              f"Parentpath: {self.parentpath} \n"
              f"Children: {self.childlist} \n"
              f"Options: {self.optionlist} \n")

    # getter and setter for child
    def set_child(self, child):
        self.childlist.append(child)

    def set_child_list(self, childlist):
        self.childlist = childlist

    def get_child(self, index=None):
        if index == None:
            return self.childlist
        else:
            return self.childlist[index]

    # getter for packagename
    def get_packagename(self):
        return self.packagename

    # getter and setter for packagepath
    def get_packagepath(self):
        return self.packagepath

    def set_packagepath(self):
        self.packagepath = find_path(self.packagename, os.getcwd())

    # getter for parentname
    def get_parenname(self):
        return self.parent

    # getter for parentepath
    def get_parentpath(self):
        return self.parentpath

    def set_option_list(self, optionlist):
        self.optionlist = optionlist

    def get_option(self, index=None):
        if index == None:
            return self.optionlist
        else:
            return self.optionlist[index]

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


# Function to find the path of a package or class
def find_path(packagename, path):
    for root, dirs, files in os.walk(path):
        if packagename in files:
            return os.path.join(root, packagename)


def split_string_by_comma(oldlist):
    newlist = []

    for items in oldlist:
        if "," in items:
            parts = items.split(",")
            newlist.extend(parts)
        else:
            newlist.append(items)

    return newlist


# Function to search the tex file for class
def search_texfile_for_class(filepath):

    pattern = r"\{(.*?)\}"

    with open(filepath, "r") as file:
        keyword = "\\documentclass"

        for lines in file:
            if keyword in lines:
                return add_ending(re.findall(pattern, lines), True)


# Function to search the tex file for packages
def search_texfile_for_packages(filepath):
    pattern = r"\{(.*?)\}"

    with open(filepath, "r") as file:
        keywords = ["\\usepackage", "\\RequirePackage", "RequirePackageWithOptions"]

        found_packages = []

        for lines in file:
            for keyword in keywords:
                if keyword in lines:
                    found_packages.append(re.findall(pattern, lines))


        flatten_list = flatten(found_packages)

        finished_list = split_string_by_comma(flatten_list)

        return add_ending(finished_list)


# Function to search for options within a tex file
def search_for_options(filepath, packagename):
    with open(filepath, "r") as file:

        pattern = r"\[(.*?)\]"

        options = []

        for lines in file:
            if packagename.strip(".sty") in lines:
                options.append(re.findall(pattern, lines))

        options = flatten(options)

        finished_list = split_string_by_comma(options)

        return filter_for_dates(finished_list)


def add_ending(list_without_endings, is_class=False):
    if is_class == True:
        return [items + ".cls" for items in list_without_endings]
    else:
        return [items + ".sty" for items in list_without_endings]


def flatten(xss):
    return [x for xs in xss for x in xs]


# Function to get the outfile from the console or use the default
def find_outfile_name(console_argument):
    if console_argument != None:
        if not console_argument.endswith(".html"):
            return console_argument + ".html"
        else:
            return console_argument
    else:
        return "graph.html"


def filter_for_dates(possible_option):
    search_patter = re.compile(r"\d\d\d\d/\d\d/\d\d")
    is_option = False

    for items in possible_option:
        option_for_search = search_patter.search(items)
        if option_for_search == None:
            is_option = True

    if is_option == True:
        return possible_option
    else:
        return []

if __name__ == "__main__":

# Startup
    parser = argparse.ArgumentParser()

    parser.add_argument("-outfile", "--outfilename", help="Name of the outfile. Should end with .html but programm will add it.")
    parser.add_argument("-s", "--sourcefile", help="Name of the sourcefile. Has to be a .tex in current directory.")
    parser.add_argument("-b", default=False, action="store_true", help="If set the outfile will be open at the end. Default is false.")

    args = parser.parse_args()

# Caching Errors in the console input
    if args.sourcefile == None:
        print("Missing sourcefile. Please give a sourcefile. \n"
              "\n"
              "Example: python3 main.py -s example.tex \n"
              "\n"
              "For further help enter: python3 ParserforDependenciesV2.py -h \n")
        sys.exit(2)

    if not args.sourcefile.endswith(".tex"):
        print("Sourcefile is not an .tex file. \n"
              "\n"
              "Please try again"
              "\n")
        sys.exit(2)

# Outfile build
    outfilename = find_outfile_name(args.outfilename)

# Building the main parent
    parent = Package(args.sourcefile, None, None)

    parent.set_packagepath()
    parent.set_child_list(search_texfile_for_packages(args.sourcefile) + search_texfile_for_class(args.sourcefile))

# Adding all the children to the parent list
    active_childlist = []

    for items in parent.childlist:
        child = Package(items, parent.packagename, parent.packagepath)
        child.set_child_list(search_texfile_for_packages(child.packagepath))
        child.set_option_list(search_for_options(child.parentpath, child.packagename))
        active_childlist.append(child)

    for items in active_childlist:
        if not items.is_child_list_empty():
            for childs in items.childlist:
                child = Package(childs, items.packagename, items.packagepath)
                child.set_option_list(search_for_options(items.packagepath, child.packagename))
                child.set_child_list(search_texfile_for_packages(child.packagepath))
                active_childlist.append(child)


    print(f"All packages requierd by {args.sourcefile} should be found. \n"
          f"\n"
          f"Inputfile has the following packages: \n",
          f"{parent.childlist} \n"
          "\n"
          "Other packages that are needed are: \n")
    for items in active_childlist:
        if not items.is_child_list_empty():
            if items.has_options():
                print(f"- Packaage {items.packagename} with the options {items.optionlist} requiers: {items.childlist}")
            else:
                print(f"- Package {items.packagename} requiers: {items.childlist}")


## Graph

    net = Network(width="100%", height=1000, directed=True, select_menu=True, filter_menu=True)
    net.add_node(parent.packagename, label=parent.packagename, color="#00ff1e", shape="circle")

    for items in active_childlist:
        net.add_node(items.packagename, label=items.packagename, shape="circle")
        net.add_edge(items.parent, items.packagename)
        if items.has_options():
            for options in items.optionlist:
                net.add_node(options, label=options,     shape="circle", color="#ffff1e")
                net.add_edge(items.packagename, options, label="has option", dashes=True, arrows="")

    net.inherit_edge_colors(False)
    net.force_atlas_2based(overlap=1)

    net.toggle_physics(False)
    net.save_graph(outfilename)

    if args.b == True:
        url = find_path(outfilename, ".")
        webbrowser.open(url, new=2)

