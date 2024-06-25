## This skript takes a LaTeX document and checks the dependencies

## Import Statements
import sys
import os
import re


class PackageClass:                                                                                                     ## Class to create Parents and know which Children are connected to the parent

    def __init__(self, name, path, parent):
        self.name = name
        self.parent = parent
        self.path = path
        self.childlist = []
        self.childpaths = []


    def addchild(self, child):
        self.childlist.append(child)
        self.childpaths.append(findfile(items + ".sty", "/usr/share/texlive/texmf-dist/tex"))


#    def printchild(self):
#        for items in self.childlist:
#            print(items)

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

def helpmessage():                                                                                                      ## Displays helpmessage if no arguments are provided
    print("Usage:", sys.argv[0], "[OPTIONS] [SEEDS] \n"
          "\n"
          "This skript will parse a LaTeX seed file and parse which \n" 
          "other files they require. Dependent files will only be \n" 
          "considered if they mathc a given regular expressin, which \n"
          "defaults to 'all'. \n " 
          "\n"
          "OPTIONS can be: \n"
          "     --outfile <name> [default is graph.tex] \n" 
          "\n"
          "Examples: \n"
          "     ParserforDependencies.py --outfile graph.tex source.tex")


def outfile(arguments):                                                                                                 ## Find outfile name and makes sure it is a .tex file. Defaults to graph.tex
    if "--outfile" in arguments:
        outfilename = arguments[arguments.index("--outfile")+1]
        if ".tex" in outfilename:
            return outfilename
        else:
            return outfilename + ".tex"
    else:
        return "graph.tex"


def flatten(xss):
    return [x for xs in xss for x in xs]

def loadseedfile(seedfile, pathgiven= False):                                                                           ## Loads the seedfile and finds the oackages loaded in the file
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

def findfile(filename, path):                                                                                           ## Function used to find the file path for later use
    for root, dirs, files in os.walk(path):
        if filename in files:
            return os.path.join(root, filename)

    return None


if __name__ == '__main__':
    if len(sys.argv) == 1:
        helpmessage()
        sys.exit(1)

    outfilename = outfile(sys.argv)

    if "--outfile" not in sys.argv:                                                                                     ## Gets teh seedfile name out of the argv dependeing on if an --options was used
        seedfile = loadseedfile(sys.argv[1])
        seedfilename = sys.argv[1]
    else:
        indexofseed = sys.argv.index("--outfile") + 2
        try:
            seedfile = loadseedfile(sys.argv[indexofseed])
            seedfilename = sys.argv[indexofseed]
        except(IndexError):                                                                                             ## Catches Error if --options was given, but no outputfile name
            print("Something went wrong. Try again (Index was out of bounce, missing outfile name?)")
            sys.exit(2)

    currentdirectory = os.getcwd()
    parent = PackageClass(seedfilename, currentdirectory + "/" + seedfilename ,None)                             ## Creates main parent

    for items in seedfile:                                                                                              ## adds children with their given paths
        parent.addchild(items)

    childs = []

    for i, items in enumerate(parent.childlist):                                                                        ## Creates child opjects
        child = PackageClass(items, parent.getchildpath(i),parent.name)
        childs.append(child)

    for items in childs:
        children = findchild(items)
        items.setchildlist(children)

    for items in childs:
        if items.childlistempty():
            print("No further packages requierd by ", items.name)
        else:
            print("Further packages requierd by ", items.name)
            for i, children in enumerate(items.childlist):
                child = PackageClass(children, items.getchildpath(i), items.name)
                childrenofchild = findchild(child)
                child.setchildlist(childrenofchild)
                childs.append(child)


    print("\n "
          "All packages requierd by", seedfilename, "should be found. \n"
          "\n"
          "Inputfile has the following packages: \n",
          parent.childlist, "\n"
          "\n"
          "Other packages that are needed are: \n")
    for items in childs:
        if not items.childlistempty():
            print("- Package", items.name ,"requiers: ",
                items.childlist)
