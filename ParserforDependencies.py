## This skript takes a LaTeX document and checks the dependencies

## Import Statements
import os
import re
import sys
import webbrowser
import argparse

from pyvis.network import Network

class PackageClass:

    def __init__(self, name, path, parent):
        self.name = name
        self.parent = parent
        self.path = path
        self.childlist = []
        self.childpaths = []


    def addchild(self, child):
        self.childlist.append(child)
        self.childpaths.append(findfile(items + ".sty", "/usr/share/texlive/texmf-dist/tex"))


    def printchildlist(self):
       print(self.childlist)

    def setchildlist(self, list):
        self.childlist = list
        for items in self.childlist:
            self.childpaths.append(findfile(items + ".sty", "/usr/share/texlive/texmf-dist/tex"))

#    def getchild(self, index):
#        return self.childlist[index]

    def getchildpath(self, index):
        return self.childpaths[index]

    def getpath(self):
        return self.path

    def tostring(self):
        print("Name: ", self.name, "\n"
              "Parent: ", self.parent, "\n"
              "Path: ", self.path, "\n"                        
              "Childlist: ", self.childlist, "\n"
              "Childpaths: ", self.childpaths, "\n")


    def childlistempty(self):
        if len(self.childlist) == 0:
            return True
        else:
            return False


def outfile(arguments):
    if "--outfile" in arguments:
        outfilename = arguments[arguments.index("--outfile")+1]
        if ".html" in outfilename:
            return outfilename
        else:
            return outfilename + ".html"
    else:
        return "graph.html"


def flatten(xss):
    return [x for xs in xss for x in xs]


def loadseedfile(seedfile, pathgiven= False):
    if pathgiven == False:
        filepath = os.path.abspath(seedfile)
    else:
        filepath = seedfile

    with open(filepath, "r") as file:
        texfile = []
        interruptline = "\\begin{document}"

        usepackage = "usepackage"
        requirepackage = "RequirePackage"
        requirepackagewithoption = "RequirePackageWithOptions"

        for lines in file:
            if usepackage in lines:
                texfile.append(lines)
            elif requirepackage in lines:
                texfile.append(lines)
            elif requirepackagewithoption in lines:
                texfile.append(lines)
            if interruptline in lines:
                break

        packages = []
        pattern = r'\{(.*?)\}'

        for items in texfile:
            packages.append(re.findall(pattern, items))

        packages = flatten(packages)

        check_list = []
        for items in packages:
            if "," in items:
                parts = items.split(",")
                check_list.extend(parts)
            else:
                check_list.append(items)

        return check_list


def findchild(Parent):
    parentpath = Parent.getpath()
    children = loadseedfile(parentpath, True)

    return children


def findfile(filename, path):
    for root, dirs, files in os.walk(path):
        if filename in files:
            return os.path.join(root, filename)

    return None


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-outfile", "--outfilename", help="Name of the outfile. Should end with .html but programm will add it.")
    parser.add_argument("-s", "--sourcefile", help="Name of the sourcefile. Has to be a .tex in current directory.")
    parser.add_argument("-b", "--browser", help="If True, programm will open the .html file at the end. If False it only gets saved.", default=False, type=bool)

    args = parser.parse_args()

    if args.sourcefile == None:
        print("Missing sourcefile. Please give a sourcefile. \n"
              "\n"
              "Example: python3 main.py -s example.tex \n"
              "\n"
              "For further help enter: python3 ParserforDependencies.py -h \n")
        sys.exit(2)

    if ".tex" not in args.sourcefile:
        print("Sourcefile is not an .tex file. \n"
              "\n"
              "Please try again"
              "\n")
        sys.exit(2)

    outfilename = args.outfilename
    if outfilename != None:
        if ".html" not in outfilename:
            outfilename = outfilename + ".html"
    else:
        outfilename = "graph.html"


    sourcefile = loadseedfile(args.sourcefile)
    sourcefilename = args.sourcefile

## Packagefinder

    currentdirectory = os.getcwd()
    parent = PackageClass(sourcefilename, currentdirectory + "/" + sourcefilename ,None)

    for items in sourcefile:
        parent.addchild(items)

    childs = []

    for i, items in enumerate(parent.childlist):
        child = PackageClass(items, parent.getchildpath(i),parent.name)
        childs.append(child)

    for items in childs:
        children = findchild(items)
        items.setchildlist(children)

    for items in childs:
        if items.childlistempty():
            print("No further packages requierd by", items.name, "\n"
                  "\n"
                  "Checking next child \n"
                  "\n")
        else:
            print("Further packages requierd by", items.name, "\n"
                  "\n"
                  "Fetching packages requierd by", items.name, "\n")

            for i, children in enumerate(items.childlist):
                child = PackageClass(children, items.getchildpath(i), items.name)
                childrenofchild = findchild(child)
                child.setchildlist(childrenofchild)
                childs.append(child)
                print("New child found:", child.name, "\n")

    print("\n"
          "All packages requierd by", sourcefilename, "should be found. \n"
          "\n"
          "Inputfile has the following packages: \n",
          parent.childlist, "\n"
          "\n"
          "Other packages that are needed are: \n")
    for items in childs:
        if not items.childlistempty():
            print("- Package", items.name ,"requiers: ",
                items.childlist)

## Graph
    net = Network(width="100%", height=1000, directed=True)
    net.add_node(parent.name, label=parent.name, color="#00ff1e", shape="circle")

    for items in childs:
        net.add_node(items.name, label=items.name, inherit_edge_colors=False, shape="circle")
        net.add_edge(items.parent, items.name)

    net.inherit_edge_colors(False)
    net.force_atlas_2based(overlap=1)

    net.toggle_physics(False)
    net.save_graph(outfilename)

    if args.browser == True:
        url = findfile(outfilename, ".")
        webbrowser.open(url, new=2)

    print("\n"
          "Outputfile with Graph has been generated. Filename is", outfilename, "\n"
          "\n"
          "Programm finished without errors \n")
