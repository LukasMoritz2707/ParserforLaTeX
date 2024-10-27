import argparse
import re
import sys
import os
import random

from pyvis.network import Network
import webbrowser

from latexcompiler import LC


node_id = 1

class Bcolors:
    OKGREEN = '\033[92m'
    HEADER = '\033[95m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    OKBLUE = '\033[94m'
    BOLD = '\033[1m'


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
"""
def change_name_for_nodes_without_changed(node:Node, upper_envs, lower_envs)
    for child in node.children:
        if child.name_changed is not True:
"""

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

    ref_pattern = r"\\(ref|cref|eqref)\{(.*?)\}"

    def travers(node):
        for line in node.content:
            matches = re.findall(ref_pattern, line)
            for match in matches:
                _, label_name = match
                if label_name in label_list:
                    ref_node = label_list[label_name]
                    ref_node.add_reference(node)

        for child in node.children:
            travers(child)

    travers(tree.root)

def find_cite(tree:Tree):

    cite_pattern = r"\\cite(?:\[[^\]]*\])?\{(.*?)\}"

    def travers(node):
        for line in node.content:
            matches = re.findall(cite_pattern, line)
            for items in matches:
                split_matches = items.split(",")
                for match in split_matches:
                    cite_node = Node(name=match, parent=node, type="cite")
                    node.children.append(cite_node)
                    cite_node.name_changed = True

        for child in node.children:
            travers(child)

    travers(tree.root)

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
                    tex_file_text.append(lines)


    return " ".join(str(item) for item in tex_file_text)

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

def read_enviorments(input_file):

    env_names = []

    with open(input_file, "r") as file:
        for lines in file:
            env_names.append(lines)

    return env_names

def format_label(label, max_length=20):
    lines = []
    for i in range(0, len(label), max_length):
        lines.append(label[i:i + max_length])
    return "\n".join(lines)

def build_graph(tree: Tree, doc_name):
    net = Network(notebook=False, height=1500, width="100%", directed=True, select_menu=True)
    node_mapping = {}
    edges = set()

    def add_node_to_graph(node: Node, parent_name=None, level=0.0):
        node_name = node.name
        label = format_label(node_name)

        if node.type == "Section":
            color = "#005400"
        elif node.name == doc_name:
            color = "#000000"
        elif "proof" in node.type.lower():
            color = "#a750b3"
        elif "theorem" in node.type.lower() or "definition" in node.type.lower():
            color = "#b00057"
        elif "cite" in node.type.lower():
            color = "#b07c57"
        else:
            color = "#5d86ff"

        net.add_node(node_name, label=label, title=node_name, color=color, level=level)

        if parent_name is not None:
            net.add_edge(parent_name, node_name, color="5d86ff")

        node_mapping[node] = node_name

        for child in node.children:
            add_node_to_graph(child, node_name, level + 2)

    add_node_to_graph(tree.root)

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
        <p><span style="color: #b00057;">&#9632;</span> Theorem</p>
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
    path = os.getcwd()

    tex_name = os.path.join(path, tex_file)
    aux_name = tex_file.removesuffix(".tex") + ".aux"

    try:
        return read_tex_file(aux_name)
    except FileNotFoundError:
        try:
            LC.compile_document(tex_engine="pdflatex", bib_engine="biber", path=tex_name, no_bib=True, folder_name="/home/lukas/Bachelorarbeit/ParserforSkript")

            clear_execs_files(tex_file)

            return read_tex_file(aux_name)

        except TypeError:
            return read_tex_file(find_path(aux_name, os.getcwd()))

def clear_execs_files(tex_file):
    log_name = tex_file.removesuffix(".tex") + ".log"
    pdf_name = tex_file.removesuffix(".tex") + ".pdf"
    out_name = tex_file.removesuffix(".tex") + ".out"
    synctexgz_name = tex_file.removesuffix(".tex") + ".synctex.gz"

    file_names = [log_name, pdf_name, out_name, synctexgz_name]

    for files in file_names:
        try:
            os.remove(files)
            print(f"File {files} was removed")
        except (FileNotFoundError, FileExistsError):
            print(f"File {files} was not found")

def get_ref_doc_label(ref_doc_list):
    for i, items in enumerate(ref_doc_list):
        if os.path.splitext(items) == ".tex":
            ref_doc_list[i] = ref_doc_list[i] + ".tex"

    label = []

    for items in ref_doc_list:
        label.append(get_label(items))

    return flatten(label)

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

    ref_pattern = r"\\(ref|cref|eqref|Cref)\{(.*?)\}"
    for line in node.content:
        matches = re.findall(ref_pattern, line)
        for match in matches:
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
        item = input("New Entry to list: (q/Q to Quit) ")

        if item.lower() == "q":
            break

        list_to_change.append(item)

    return list_to_change

def main_menu():
    print(f"\n--- Hauptmenü ---\n"
    f"Welche Liste möchtest du ändern?\n"
    f"1: Theoremlike\n"
    f"2: NonTrackingEnvironments\n"
    f"3: Prooflike\n"
    f"4: Show list\n"
    f"q: Quit\n")
    print("-" * 30)


def list_menu(upper_envs, banned_envs, lower_envs):
    print("\n--- Show List ---")
    print("Current content:\n")

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

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--inputfile", help="This file is the document you want to be searched")
    parser.add_argument("-l", default=False, action="store_true", help="If set it will return a list of Labels that are used in the document, including orphand labels.")
    parser.add_argument("-t", default=False, action="store_true", help="If set it will return the Treestructure in the Konsole")
    parser.add_argument("-b", default=True, action="store_false", help="If set the graph will not be opened in the browser")
    parser.add_argument("-g", "--graph_name", help="Custom name for the Graph")
    parser.add_argument("-e", default=False, action="store_true", help="Gives the option to add custom environments to the default lists")

    args = parser.parse_args()

    # Caching Errors in the console input
    if args.inputfile == None:
        print("Missing sourcefile. Please give a sourcefile. \n"
              "\n"
              "Example: python3 ParserforSkript.py -i example.tex \n"
              "\n"
              "For further help enter: python3 ParserforSkrip.py -h \n")
        sys.exit(1)

    upper_envs = ["definition", "theorem", "lemma", "proposition", "corollary"]
    banned_envs = ["enumerate", "itemize"]
    lower_envs = ["proof"]

    if args.e:
        while True:
            main_menu()
            console = input("Which list do you whant to change? ")
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
    tex_file_text = read_tex_file(doc_name)

    reference_documents = get_ref_doc(tex_file_text)
    ref_labels = get_ref_doc_label(reference_documents)

    tree = Tree(doc_name)

    current_section = None
    current_environment = None

    last_upper_env = None

    for line in tex_file_text.splitlines():
        section_match = re.search(r'\\(section|subsection|subsubsection|chapter)\*?\s*\{(.+?)\}', line)
        begin_env_match = re.search(r'\\begin\{(\w+)\}(?:\[(.*?)\])?', line)
        end_env_match = re.search(r'\\end\{(\w+)\}', line)

        if section_match:
            section_title = section_match.group(2).strip()
            section_level = section_match.group(1).strip()
            if section_level != "section":
                section_node = Node(section_title, type="Section")
                current_section.add_child(section_node)
                current_environment = section_node
            else:
                current_section = tree.add_section(section_title)
                current_environment = None
            last_upper_env = None

        if begin_env_match:
            env_name = begin_env_match.group(1).strip()
            env_title = begin_env_match.group(2)


            if env_name in upper_envs:
                env_node = Node(env_name, subtitle=env_title if env_title else None)
                if current_section:
                    current_section.add_child(env_node)
                else:
                    current_environment.add_child(env_node)
                current_environment = env_node
                last_upper_env = env_node

            elif env_name in banned_envs:
                pass

            elif env_name in lower_envs:
                env_node = Node(env_name, subtitle=env_title if env_title else None)
                if last_upper_env:
                    last_upper_env.add_child(env_node)
                else:
                    pass
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

    append_label(tree.root)
    append_numbers(tree.root, aux_file)
    change_title(tree.root)
    append_proof(tree.root, upper_envs, lower_envs)
    find_cite(tree)

    labels_in_doc = extract_label(tree)

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


    graph = build_graph(tree, doc_name)

    graph_name = plot_graph(graph, graph_name=graph_name if graph_name else "graph.html")

    if args.b == True:
        webbrowser.open(graph_name, new=2)
