import os
import re
import sys
import webbrowser
import argparse

import networkx as nx
from networkx.drawing.nx_pydot import write_dot
from prompt_toolkit.cache import memoized

from pyvis.network import Network

counter = 1

class Bcolors:
    OKGREEN = '\033[92m'
    HEADER = '\033[95m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    OKBLUE = '\033[94m'
    BOLD = '\033[1m'

class Node():

    def __init__(self, name, parentname, test_package=False, path=None):
        self.name = name
        self.path = (path if test_package else find_path(self.name, "/usr/share/texlive/texmf-dist/tex/"))
        self.parent = parentname
        self.childlist = []
        self.optionlist = []
        self.inputlist = []
        self.refrenzlist = []

    def set_path(self, path):
        self.path = path

    def set_inputlist(self, liste):
        for items in liste:
            self.inputlist.append(Node(items, self.name))

    def to_string(self):
        print(f"Name: {self.name} \n"
              f"Path: {self.path} \n"
              f"Parent: {self.parent} \n"
              f"Children:")
        for items in self.childlist:
            print(items.name)
        print(f"Options: {self.optionlist} \n"
              f"Inputs:")
        for items in self.inputlist:
            print(items.name)
        print("Refrenzes:")
        for items in self.refrenzlist:
            print(items.name)


    def is_child_list_empty(self):
        if len(self.childlist) == 0:
            return True
        else:
            return False

    def print_inputlist(self):
        new_list = []
        for items in self.inputlist:
            new_list.append(items.name)
        return new_list

    def print_childlist(self):
        new_list = []
        for items in self.childlist:
            new_list.append(items.name)
        return new_list

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
    try:
        return open(file, "r", encoding="utf-8").read()
    except UnicodeDecodeError:
        return open(file, "r", encoding="ISO-8859-1").read()


def find_path(packagename, path):
    for root, dirs, files in os.walk(path):
        if packagename in files:
            return os.path.join(root, packagename)

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

    split_by_comma = split_string_by_comma(found_patterns)
    found_patterns = []

    if isinstance(split_by_comma, list):
        for i in range(0, len(split_by_comma)):
            if isinstance(split_by_comma[i], tuple):
                new_tuple = (split_by_comma[i][0], split_by_comma[i][1] + ".sty")
                found_patterns.append(new_tuple)
            else:
                found_patterns.append(split_by_comma[i] + ".sty")
    else:
        found_patterns = split_by_comma + ".sty"

    return found_patterns

def check(name, processed_packages):
    if not ("#" in name or name == ".sty") and name not in processed_packages:
        return True
    else:
        return False

@memoized(maxsize=128)
def process_children(node: Node, processed_packages=None, ref_list=(), test=False, test_length=None):
    if processed_packages is None:
        processed_packages = frozenset()

    ref_list = dict(ref_list)

    processed_list = list(processed_packages)

    for child in node.childlist:
        if child.path is None:
            continue

        if test:
            global counter
            print(f"Currently working on: {child.name} ({counter} of approx. {test_length})")
            counter += 1

        file = read_file(child.path)
        packages = extract_package_infomation(file)

        for item in packages:
            if isinstance(item, tuple):
                options, package = item
                if check(package, processed_packages):
                    new_child = Node(package, child.name)
                    new_child.optionlist.append(options)
                    child.childlist.append(new_child)
                    processed_list.append(package)
                    ref_list[new_child.name] = new_child
                elif package in processed_packages:
                    child.refrenzlist.append(ref_list[package])
            else:
                if check(item, processed_packages):
                    new_child = Node(item, child.name)
                    child.childlist.append(new_child)
                    processed_list.append(item)
                    ref_list[new_child.name] = new_child
                elif item in processed_packages:
                    child.refrenzlist.append(ref_list[item])

        for input_file in node.inputlist:
            process_children(input_file, frozenset(processed_list), tuple(ref_list.items()), test, test_length)

        process_children(child, frozenset(processed_list), tuple(ref_list.items()), test, test_length)


def build_graph(node: Node):
    net = Network(notebook=False, height=1500, width="100%", directed=True, select_menu=True, neighborhood_highlight=True, filter_menu=True)
    node_mapping = {}
    edges = set()

    def add_node_to_graph(node: Node, parent_name=None):
        node_name = node.name.replace(":", "")

        net.add_node(node_name, label=node_name.strip(":"), title=node_name, color="green" if ".cls" in node_name else None)

        if parent_name is not None:
            edge = (parent_name, node_name)
            if edge not in edges:
                net.add_edge(parent_name, node_name, color="5d86ff", label=node.optionlist.__str__() if node.has_options() else None)
                edges.add((parent_name, node_name))

        node_mapping[node] = node_name

        for child in node.childlist:
            add_node_to_graph(child, node_name)

    add_node_to_graph(node)

    for node, node_name in node_mapping.items():
        for ref_node in set(node.refrenzlist):
            edge = (node_name, ref_node.name)
            if ref_node in node_mapping and edge not in edges:
                ref_node_name = node_mapping[ref_node]
                net.add_edge(node_name, ref_node_name, color="5d86ff")
                edges.add(edge)

    return net

def plot_graph(net, graph_name, main_parent):
    net.get_node(main_parent.name)["color"] = '#FFFF33'


    net.inherit_edge_colors(False)
    net.barnes_hut(gravity=-2000, overlap=0.5)

    net.toggle_physics(True)
    net.save_graph(graph_name)

    print(f"\n"
          f"Outputfile with Graph has been generated. Filename is {graph_name} \n")

    if args.b == True:
        url = find_path(graph_name, ".")
        webbrowser.open(url, new=2)
        print("The graph was opened in your browser \n")

def extract_class_infomation(file):
    pattern = regex_class_pattern()

    found_patterns = []
    for patterns in pattern:
        found_patterns.extend(re.findall(patterns,file))

    split_by_comma = split_string_by_comma(found_patterns)
    found_patterns = []

    if isinstance(split_by_comma, list):
        for i in range(0, len(split_by_comma)):
            if isinstance(split_by_comma[i], tuple):
                new_tuple = (split_by_comma[i][0], split_by_comma[i][1] + ".cls")
                found_patterns.append(new_tuple)
            else:
                found_patterns.append(split_by_comma[i] + ".cls")
    else:
        found_patterns = split_by_comma + ".cls"

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

def print_all_children(parent):
    for child in parent.childlist:
        if not child.is_child_list_empty():
            printable_childlist = child.print_childlist()
            if child.has_options():
                print(f"- Package {child.name} with the options {child.optionlist} requires: {printable_childlist}")
            else:
                print(f"- Package {child.name} requires: {printable_childlist}")

            print_all_children(child)

def append_packages_to_file(objects, node:Node):
    if type(objects) is tuple:
        option, tex_class = objects
        option = split_string_by_comma(option)
        tex_class = split_string_by_comma(tex_class)
        for elements in tex_class:
            child = Node(elements, node.name)
            child.optionlist.append(option)
            node.childlist.append(child)
    else:
        child = Node(objects, node.name)
        node.childlist.append(child)

def test_all_packages():
    all_packages = []
    path = "/usr/share/texlive/texmf-dist/tex/"
    graph_name = "all_packages_test_graph.html"

    for root, dirs, files in os.walk(path):
        for name in files:
            if ".sty" in name or ".cls" in name:
                all_packages.append((name, os.path.abspath(os.path.join(root, name))))

    main_parent = Node("Source", None)
    main_parent.set_path(None)

    number_packages = len(all_packages)

    helper_level_1 = []
    helper_level_2 = []
    helper_level_3 = []

    for i in range(10):
        helper_node = Node(f"Helper {i + 1}", parentname=main_parent, test_package=True)
        main_parent.childlist.append(helper_node)
        helper_level_1.append(helper_node)

    for nodes in helper_level_1:
        for i in range(10):
            helper_node = Node(f"Helper for {nodes.name} {i + 1}", parentname=main_parent, test_package=True)
            nodes.childlist.append(helper_node)
            helper_level_2.append(helper_node)

    for nodes in helper_level_2:
        for i in range(10):
            helper_node = Node(f"Helper for {nodes.name} {i + 1}", parentname=main_parent, test_package=True)
            nodes.childlist.append(helper_node)
            helper_level_3.append(helper_node)

    helper_index = 0
    for i, (name, path) in enumerate(all_packages):
        current_helper_node = helper_level_3[helper_index]
        current_helper_node.childlist.append(Node(name, parentname=current_helper_node, test_package=True, path=path))

        if len(current_helper_node.childlist) >= 7:
            helper_index += 1

    print(f"Number of all Packages: {number_packages}")

    for nodes in helper_level_3:
        process_children(nodes, test=True, test_length=number_packages * 20)

    net = build_graph(main_parent)

    plot_graph(net, graph_name, main_parent),

    print("Size of network: ", net.num_nodes())

    adjenzlist = net.get_adj_list()

    # Dot
    Graph = nx.DiGraph(adjenzlist)
    write_dot(Graph, "all_packages_test_graph.dot")
    print("A DOT file was created containg the graph")


if __name__ == "__main__":

# Startup
    parser = argparse.ArgumentParser()

    parser.add_argument("-outfile", "--outfilename", help="Name of the outfile. Should end with .html but programm will add it.")
    parser.add_argument("-s", "--sourcefile", help="Name of the sourcefile. Has to be a .tex in current directory.")
    parser.add_argument("-b", default=True, action="store_false", help="If set the outfile will not be opened at the end. Default is true.")
    parser.add_argument("-i", default=False, action="store_true", help="If set \\include and \\input while be ignored.")
    parser.add_argument("-pipe", default=False, action="store_true", help="Uses a adjazenzlist to generate a graph in a .DOT format")
    parser.add_argument("-test", default=False, action="store_true")

    args = parser.parse_args()

    if args.test == True:
        test_all_packages()
        sys.exit(0)

# Caching Errors in the console input
    if args.sourcefile == None:
        print("Missing sourcefile. Please give a sourcefile. \n"
              "\n"
              "Example: python3 ParserforPackages.py -s example.tex \n"
              "\n"
              "For further help enter: python3 ParserforPackages.py -h \n")
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

    main_parent = Node(args.sourcefile, None)
    main_parent.set_path(find_path(args.sourcefile, os.getcwd()))

    if args.i is False:
            main_parent.set_inputlist(extract_input_information(file))
            for items in main_parent.inputlist:
                packages_in_inputs = extract_package_infomation(read_file(items.name))
                for objects in packages_in_inputs:
                    append_packages_to_file(objects, items)

    for items in tex_class:
        append_packages_to_file(items, main_parent)

    for items in packages:
        append_packages_to_file(items, main_parent)

    #print("Aufruf vor Hauptaufruf")
    #main_parent.to_string()

# Hauptaufruf
    process_children(main_parent)

    printable_childlist = main_parent.print_childlist()
    printable_inputlist = main_parent.print_inputlist()

    #print_all_children(parent=main_parent)

# Output on Console
    print(f"\n"
          f"All packages for {args.sourcefile} where found. \n"
          f"\n"
          f"Inputfile has the following packages: \n"
          f"{printable_childlist}"
          f"\n"
          f"Other packages requierd are: \n")
    print_all_children(main_parent)

    if args.i == False:
        if main_parent.has_inputs():
            print(f"\n"
                  f"Inputs in {main_parent.name} are:\n"
                  f"{printable_inputlist}")

            print(f"\n"
                  f"Packages in Inputfiles are: \n")

# Graph

#    net = Network(width="100%", height=1000, directed=True, select_menu=True, filter_menu=True)

#    net = add_nodes_and_edges(net, main_parent)

    net = build_graph(main_parent)

    plot_graph(net, graph_name=outfilename, main_parent=main_parent)

    if args.pipe == True:
        adjenzlist = net.get_adj_list()

        # Dot
        Graph = nx.DiGraph(adjenzlist)
        write_dot(Graph, "graph.dot")
        print("A DOT file was created containg the graph")

    print("Program finished without errors \n")
