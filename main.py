## This skript takes a LaTeX document and checks the dependencies

## Import Statements
import sys
import os


class PackageClass:                                                                                                     ## Class to create Parents and know which Children are connected to the parent

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.childlist = []
        self.childpaths = []


    def addchild(self, child):
        self.childlist.append(child)
        self.childpaths.append(findfile(items + ".sty", "/usr/share/texlive/texmf-dist/tex"))


    def printchild(self):
        for items in self.childlist:
            print(items)


    def tostring(self):
        print("Name: ", self.name, "\n"
              "Parent: ", self.parent, "\n"
              "Childlist: ", self.childlist, "\n"
              "Childpaths: ", self.childpaths, "\n")


def helpmessage():                                                                                                      ## Displays helpmessage if no arguments are provided
    print("Usage: ParserforDependencies.py [OPTIONS] [SEEDS] \n"
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


def loadseedfile(seedfile):                                                                                             ## Loads the seedfile and finds the oackages loaded in the file
    filepath = os.path.abspath(seedfile)

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

        for items in texfile:
            packages.append(items.strip("\\ \n usepackage RequirePackage RequirePackageWithOptions"))

        for n in range(0, len(packages)):
            packages[n] = packages[n].strip("{ }")

        return packages


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

    parent = PackageClass(seedfilename, None)                                                                     ## Creates main parent

    for items in seedfile:                                                                                              ## adds children with their given paths
        parent.addchild(items)

    childs = []

    for items in parent.childlist:                                                                                      ## Creates child opjects
        child = PackageClass(items, parent.name)
        childs.append(child)

    parent.tostring()

    for items in childs:
        items.tostring()