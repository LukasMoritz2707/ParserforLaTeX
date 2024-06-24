## This skript takes a LaTeX document and checks the dependencies

## Import Statements
import sys
import os

def helpmessage():
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


def outfile(arguments):
    if "--outfile" in arguments:
        outfilename = arguments[arguments.index("--outfile")+1]
        if ".tex" in outfilename:
            return outfilename
        else:
            return outfilename + ".tex"
    else:
        return "graph.tex"


def loadseedfile(seedfile):
    filepath = os.path.abspath(seedfile)
    with open(filepath, "r") as file:

        texfile = []
        interruptline = "\\begin{document}"

        for lines in file:
            texfile.append(lines.strip(" "))
            if interruptline in lines:
                break

        return texfile


if __name__ == '__main__':
    if len(sys.argv) == 1:
        helpmessage()
        sys.exit(1)

    outfilename = outfile(sys.argv)
    if "--outfile" not in sys.argv:
        seedfile = loadseedfile(sys.argv[1])
    else:
        indexofseed = sys.argv.index("--outfile") + 2
        try:
            seedfile = loadseedfile(sys.argv[indexofseed])
        except(IndexError):
            print("Something went wrong. Try again (Index was out of bounce, missing outfile name?)")


    ## Start of extraxtion
    print(seedfile)
