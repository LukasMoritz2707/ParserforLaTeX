#!/usr/bin/env python3
import argparse
import re
import sys
import os
import networkx as nx
from networkx.drawing.nx_pydot import write_dot

from pyvis.network import Network
import webbrowser



node_id = 1

class Bcolors:
    OKGREEN = '\033[92m'
    HEADER = '\033[95m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    OKBLUE = '\033[94m'
    BOLD = '\033[1m'

class Level:

    def __init__(self):
        self.type = None

    def set_level(self, level):
        self.type = level

class Node:

    def __init__(self, name,parent=None, subtitle=None, type=None):
        self.name = name
        self.subtitle = subtitle
        self.env_name = name
        self.children = []
        self.content = []
        self.label = None
        self.references = []
        self.number = None
        self.parent = parent
        self.type = name if type == None else type
        self.name_changed = False

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def add_content(self, text):
        self.content.append(text)

    def add_label(self, label):
        self.label = label

    def add_reference(self, node):
        self.references.append(node)

    def add_number(self, number):
        self.number = number

class Tree:

    def __init__(self, name):
        self.root=Node(name)

    def add_section(self, name):
        section_node = Node(name, type="Section")
        self.root.add_child(section_node)
        return section_node

def print_tree(node:Node, level=0, prefix=""):

    indent = " " * (4* level) + prefix

    print(indent + "Node:", Bcolors.FAIL, node.name, Bcolors.ENDC)
    #, " " , Bcolors.OKGREEN, node.label, " ", Bcolors.OKBLUE, node.subtitle, Bcolors.HEADER, node.parent, "Content: ", node.content

    child_prefix = "|-- " if len(node.children) > 1 else "`-- "

    for i, child in enumerate(node.children):
        next_prefix = child_prefix if i < len(node.children) - 1 else "`-- "
        print_tree(child, level + 1, next_prefix)

def print_env_content(node:Node):

    for child in node.children:
        print(f"Aktuelle Node: {child.name}\n"
              f"\n"
              f"Inhalt: {child.content}\n"
              f"\n")
        print_env_content(child)

def change_type(node:Node, upper_envs, lower_envs):
    for child in node.children:
        if child.type.lower() in upper_envs:
            child.type = "Theoremlike"
        elif child.type.lower() in lower_envs:
            child.type = "Proof"

        change_type(child, upper_envs, lower_envs)

def change_title(node:Node):

    global node_id

    for child in node.children:
        if child.number is not None and child.label is not None:
            if child.subtitle is not None:
                child.name =  child.name + " " + child.number  + " "+ child.subtitle + " " + child.label.split(":")[1]
                child.name_changed = True
            else:
                child.name = child.name + " " + child.number + " " + child.label.split(":")[1]
                child.name_changed = True
        elif child.label is not None:
            if child.subtitle is not None:
                child.name = child.name + " " + child.subtitle + " " + child.label.split(":")[1]
                child.name_changed = True
        else:
            if child.subtitle is not None:
                child.name = child.name + " "+ child.subtitle
                child.name_changed = True

        if child.name_changed == False:
            parent = child.parent
            while parent is not None and parent.env_name not in upper_envs:
                parent = parent.parent

            if parent is not None:
                child.name = node_id.__str__() + " " + child.name + " for " + parent.name
                node_id += 1
                child.name_changed = True

            if parent is None:
                child.name = node_id.__str__() + " " + child.name + " for " + child.parent.name
                node_id += 1
                child.name_changed = True

        change_title(child)

def append_proof(node:Node, upper_envs, lower_envs):
    for child in node.children:
        if child.name in lower_envs:
            parent = child.parent
            while parent is not None and parent.env_name not in upper_envs:
                parent = parent.parent

            if (parent is not None and parent.env_name in upper_envs):
                child.name = "Proof for " + parent.name
                child.name_changed = True

        append_proof(child, upper_envs, lower_envs)

def append_label(node:Node):

    pattern = r"\\label\{([^\}]+)\}"

    for child in node.children:
        for line in child.content:
            match = re.search(pattern, line)
            if match:
                label = match.group(1)
                child.add_label(label)

        append_label(child)

def extract_label(tree):
    labels = {}

    def travers(node):
        if node.label:
            labels[node.label] = node

        for child in node.children:
            travers(child)

    travers(tree.root)
    return labels

def connect_envs(tree:Tree, label_list):

    ref_pattern = r"\\(ref|cref|eqref|Cref)\{(.*?)\}|\\hyperref\[(.*?)\]"

    def travers(node):
        for line in node.content:
            matches = re.findall(ref_pattern, line)
            for match in matches:
                _, _, label_name = match
                if label_name in label_list:
                    ref_node = label_list[label_name]
                    ref_node.add_reference(node)

        for child in node.children:
            travers(child)

    travers(tree.root)

def find_cite(node:Node):

    cite_pattern = r"\\cite(?:\[[^\]]*\])?\{(.*?)\}"

    for child in node.children:
        for line in child.content:
            matches = re.findall(cite_pattern, line)
            for items in matches:
                split_matches = items.split(",")
                for match in split_matches:
                    cite_node = Node(name=match, parent=node, type="cite")
                    child.children.append(cite_node)
                    cite_node.name_changed = True


        find_cite(child)

def find_path(filename, path):
    for root, dirs, files in os.walk(path):
        if filename in files:
            return os.path.join(root, filename)

def regex_input_pattern():
    pattern = [r"\\input\s*\{\s*(.*?)\s*\}",
               r"\\include\s*\{\s*(.*?)\s*\}"]

    return pattern

def extract_input_information(file):
    pattern = regex_input_pattern()

    found_patterns = []
    for patterns in pattern:
        found_patterns.extend(re.findall(patterns, file))

    for i, items in enumerate(found_patterns):
        if not os.path.splitext(items)[1]:
            found_patterns[i] = items + ".tex"

    return found_patterns[0]

def read_tex_file(file):

    tex_file_text = []
    preämbel = []
    text_has_began = False

    with open(file, "r") as file:
        for lines in file:
            if text_has_began == True:
                if "\\input" in lines or "\\include" in lines:
                    try:
                        with open(extract_input_information(lines)) as file:
                            tex_file_text.append(file.read())
                    except FileNotFoundError:
                        try:
                            path = find_path(extract_input_information(lines), os.getcwd())
                            with open(path, "r") as file:
                                tex_file_text.append(file.read())
                        except FileNotFoundError:
                            print(f"Did not find File {lines} on PC")
                else:
                    tex_file_text.append(lines)
            else:
                if "\\begin{document}" in lines:
                    text_has_began = True
                    tex_file_text.append(lines)
                else:
                    preämbel.append(lines)

    return " ".join(str(item) for item in tex_file_text), " ".join(str(item) for item in preämbel)

def append_numbers(node:Node, aux_file):

    pattern = r"^\\newlabel\{(.+?)\}\{\{(.*?)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}\}"

    with open(aux_file, "r") as file:
        for lines in file:
            match = re.search(pattern, lines)
            if match:
                label_name = match.group(1)
                number = match.group(2)
                add_number_to_node(node, label_name, number)

def add_number_to_node(node:Node, label_name, number):
    if node.label == label_name:
        node.number = number

    for child in node.children:
        add_number_to_node(child, label_name, number)

def format_label(label, max_length=20):
    lines = []
    for i in range(0, len(label), max_length):
        lines.append(label[i:i + max_length])
    return "\n".join(lines)

def build_graph(node: Node, doc_name):
    net = Network(notebook=False, height=1500, width="100%", directed=True, select_menu=True, neighborhood_highlight=True, filter_menu=True)
    node_mapping = {}
    edges = set()

    def add_node_to_graph(node: Node, parent_name=None, level=0.0):
        node_name = node.name.replace(":", " ")
        label = format_label(node_name)

        if node.type == "Section":
            color = "#005400"
        elif node.name == doc_name:
            color = "#000000"
        elif node.type.lower() == "proof":
            color = "#a750b3"
        elif node.type.lower() == "theoremlike":
            color = "#b00057"
        elif "cite" in node.type.lower():
            color = "#b07c57"
        else:
            color = "#5d86ff"

        net.add_node(node_name, label=label.strip(":"), title=node_name, color=color, level=0.0 if node.type == "Refdoc" else level, type=node.type)

        if parent_name is not None:
            net.add_edge(parent_name, node_name, color="5d86ff")

        node_mapping[node] = node_name

        for child in node.children:
            add_node_to_graph(child, node_name, level + 2)

    add_node_to_graph(node)

    for node, node_name in node_mapping.items():
        for ref_node in node.references:
            edge = (node_name, ref_node)
            if ref_node in node_mapping and edge not in edges:
                ref_node_name = node_mapping[ref_node]
                net.add_edge(ref_node_name, node_name, color="red")
                edges.add(edge)

    net.inherit_edge_colors(False)

    return net


def plot_graph(net, graph_name):
    net.set_options("""
        {
          "layout": {
            "hierarchical": {
              "enabled": true,
              "levelSeparation": 400,
              "nodeSpacing": 300,
              "treeSpacing": 300,
              "direction": "UD",
              "sortMethod": "directed"
            }
          },
          "physics": {
            "hierarchicalRepulsion": {
              "nodeDistance": 400     
            },
            "minVelocity": 0.75
          },
          "edges": {
            "inherit": false,
            "smooth": {
              "enabled": true,
              "type": "cubicBezier",
              "forceDirection": "none"
            }
          }
        }
    """)

    net.save_graph(graph_name)

    add_legend_to_graph(graph_name)
    return (graph_name)

def add_legend_to_graph(graph_name):

    legende="""
    <div style="position: absolute; top: 10px; right: 10px; background-color: white; padding: 10px; border: 1px solid black; z-index: 1000;">
        <h3>Legende</h3>
        <p><span style="color: #b00057;">&#9632;</span> Theoremlike</p>
        <p><span style="color: #a750b3;">&#9632;</span> Beweis</p>
        <p><span style="color: #005400;">&#9632;</span> Kapitel</p>
        <p><span style="color: #b07c57;">&#9632;</span> Zitate</p>
    </div>
    """

    with open(graph_name, "r") as file:
        html_content = file.read()

    new_conent = html_content.replace("<body>", "<body>" + legende)

    with open(graph_name, "w") as file:
        file.write(new_conent)

def get_label(tex_file):
    aux_file_text = read_aux_file(tex_file)

    pattern = r"\\newlabel\{(.*?)\}"

    found_labels = []

    for lines in aux_file_text.splitlines():
        found_labels.append(re.findall(pattern, lines))

    flatten_label = flatten(found_labels)

    cleand_label = []

    for items in flatten_label:
        if "@cref" not in items:
            cleand_label.append(items)

    return cleand_label

def flatten(xss):
    return [x for xs in xss for x in xs]

def read_aux_file(tex_file):

    aux_name = get_aux_name(tex_file)

    try:
        _, aux_file = read_tex_file(aux_name)
        return aux_file
    except FileNotFoundError:
        print("Aux File could not be found.")
        sys.exit(1)

def get_ref_doc_label(ref_doc_list, node: Node):
    labels = {}

    for i, items in enumerate(ref_doc_list):
        if os.path.splitext(items) != ".tex":
            ref_doc_list[i] = ref_doc_list[i] + ".tex"

    for items in ref_doc_list:
        label = get_label(items)
        for item in label:
            labels[item] = get_node_with_name(node, items.removesuffix(".tex"))

    return labels

def get_node_with_name(node:Node, name):
    for children in node.children:
        if children.name == name:
            return children

def get_ref_doc(main_document):

    pattern = r"\\externaldocument\{(.*?)\}"

    found_docs = []

    for lines in main_document.splitlines():
        if "\\externaldocument" in lines:
            found_docs.append(re.findall(pattern, lines))

    return flatten(found_docs)

def get_aux_name(tex_file):
    return tex_file.removesuffix(".tex") + ".aux"

def collect_labels_and_refs(node:Node, label_set, ref_set):
    if node.label:
        label_set.add(node.label)

    ref_pattern = r"\\(ref|cref|eqref|Cref)\{(.*?)\}|\\hyperref\[(.*?)\]"

    for line in node.content:
        matches = re.findall(ref_pattern, line)
        for match in matches:
            print(match[0], match[1])
            ref_set.add(match[1])

    for child in node.children:
        collect_labels_and_refs(child, label_set, ref_set)

def find_orphaned_labels(tree:Tree):
    label_set = set()
    ref_set = set()

    collect_labels_and_refs(tree.root, label_set, ref_set)

    orphand_labels = label_set - ref_set

    return orphand_labels

def change_list(list_to_change):
    while True:
        item = input("Neuer Eintrag: (q/Q zum Beenden) ")

        if item.lower() == "q":
            break

        list_to_change.append(item)

    return list_to_change

def main_menu():
    print("\n--- Hauptmenü ---\n"
    "Welche Liste möchtest du ändern?\n"
    "1: Theoremlike\n"
    "2: NonTrackingEnvironments\n"
    "3: Prooflike\n"
    "4: Show list\n"
    "q: Quit\n")
    print("-" * 30)


def list_menu(upper_envs, banned_envs, lower_envs):
    print("\n--- Show List ---")
    print("Aktueller Inhalt:\n")

    print("Theoremlike:")
    print_list(upper_envs)

    print("\nNonTrackingEnvironments:")
    print_list(banned_envs)

    print("\nProoflike:")
    print_list(lower_envs)
    print("-" * 30)

def print_list(lst):
    for index, item in enumerate(lst, 1):
        print(f"  {index}. {item}")

def process_script(tree:Tree, tex_file_text, upper_envs, banned_envs, lower_envs):
    current_section = None
    current_environment = None
    last_upper_env = None
    upper_section_level = Level()

    for line in tex_file_text.splitlines():
        section_match = re.search(r'\\(section|subsection|subsubsection|chapter)\*?\s*\{(.+?)\}', line)
        begin_env_match = re.search(r'\\begin\{(\w+)\}(?:\[(.*?)\])?', line)
        end_env_match = re.search(r'\\end\{(\w+)\}', line)

        if section_match:
            section_title = section_match.group(2).strip()
            section_level = section_match.group(1).strip()
            if upper_section_level.type is None:
                upper_section_level.set_level(section_level)
            if section_level == upper_section_level.type:
                current_section = tree.add_section(section_title)
                current_environment = None
            else:
                section_node = Node(section_title, type="Section")
                current_section.add_child(section_node)
                current_environment = section_node
            last_upper_env = None

        if begin_env_match:
            env_name = begin_env_match.group(1).strip()
            env_title = begin_env_match.group(2)

            if env_name in upper_envs:
                env_node = Node(env_name, subtitle=env_title if env_title else None, type="Theoremlike")
                if current_section:
                    current_section.add_child(env_node)
                else:
                    current_environment.add_child(env_node)
                current_environment = env_node
                last_upper_env = env_node

            elif env_name in banned_envs:
                pass

            elif env_name in lower_envs:
                env_node = Node(env_name, subtitle=env_title if env_title else None, type="Proof")
                if last_upper_env:
                    last_upper_env.add_child(env_node)
                else:
                    current_environment.add_child(env_node)
                current_environment = env_node

            else:
                if current_environment:
                    env_node = Node(env_name, subtitle=env_title if env_title else None)
                    current_environment.add_child(env_node)
                    current_environment = env_node
                elif current_section:
                    env_node = Node(env_name, subtitle=env_title if env_title else None)
                    current_section.add_child(env_node)
                    current_environment = env_node

        if end_env_match:
            env_name = end_env_match.group(1).strip()
            if env_name not in banned_envs:
                if current_environment is not None and current_environment.parent is not None:
                    current_environment = current_environment.parent
                else:
                    current_environment = None
            else:
                pass

        if current_environment:
            current_environment.add_content(line)
        elif current_section:
            current_section.add_content(line)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--inputfile", help="This file is the document you want to be searched")
    parser.add_argument("-l", default=False, action="store_true", help="If set it will return a list of Labels that are used in the document, including orphand labels.")
    parser.add_argument("-t", default=False, action="store_true", help="If set it will return the Treestructure in the Konsole")
    parser.add_argument("-b", default=True, action="store_false", help="If set the graph will not be opened in the browser")
    parser.add_argument("-g", "--graph_name", help="Custom name for the Graph")
    parser.add_argument("-e", default=False, action="store_true", help="Gives the option to add custom environments to the default lists")
    parser.add_argument("-pipe", default=False, action="store_true", help="Uses a adjazenzlist to generate a graph in a .DOT format")

    args = parser.parse_args()

    # Caching Errors in the console input
    if args.inputfile == None:
        print("Missing sourcefile. Please give a sourcefile. \n"
              "\n"
              "Example: python3 Parserforscript.py -i example.tex \n"
              "\n"
              "For further help enter: python3 Parserforscript.py -h \n")
        sys.exit(1)

    upper_envs = []
    banned_envs = ["minted", "tikzpicture", "align", "tabular", "minipage"]
    lower_envs = []

    if args.e:
        while True:
            main_menu()
            console = input("Welche Liste soll geändert werden? ")
            if console == "1":
                upper_envs = change_list(upper_envs)
            elif console == "2":
                banned_envs = change_list(banned_envs)
            elif console == "3":
                lower_envs = change_list(lower_envs)
            elif console == "4":
                list_menu(upper_envs, banned_envs, lower_envs)
            elif console.lower() == "q":
                break
            else:
                print("Invalid Entry. Try again")

    doc_name = args.inputfile
    graph_name = args.graph_name if args.graph_name else None
    aux_file = get_aux_name(doc_name)
    tex_file_text, preämble = read_tex_file(doc_name)

    reference_documents = get_ref_doc(preämble)

    tree = Tree(doc_name)

    for items in reference_documents:
        ref_node = Node(items, parent=None, subtitle=None, type="Refdoc")
        ref_node.name_changed = True
        tree.root.add_child(ref_node)

    ref_labels = get_ref_doc_label(reference_documents, tree.root)

    process_script(tree, tex_file_text, upper_envs, banned_envs, lower_envs)

    append_label(tree.root)
    append_numbers(tree.root, aux_file)
    change_title(tree.root)
    append_proof(tree.root, upper_envs, lower_envs)
    find_cite(tree.root)
    change_type(tree.root, upper_envs, lower_envs)

    labels_in_doc = extract_label(tree) | ref_labels

    connect_envs(tree, labels_in_doc)

    if args.l == True:
        print("Labels used in the document are: \n")
        for items in labels_in_doc:
            print(items)
        print("\n")

        orphand_labels = find_orphaned_labels(tree)

        print("Orphand Labels are:")
        for labels in orphand_labels:
            print(labels)

        print("\n")

    if args.t == True:
        print_tree(tree.root)


    graph = build_graph(tree.root, doc_name)

    graph_name = plot_graph(graph, graph_name=graph_name if graph_name else "graph.html")

    if args.b == True:
        webbrowser.open(graph_name, new=2)

    if args.pipe == True:
        adjenzlist = graph.get_adj_list()

        Graph = nx.DiGraph(adjenzlist)
        write_dot(Graph, "graph.dot")
        print("A DOT file was created containg the graph")
