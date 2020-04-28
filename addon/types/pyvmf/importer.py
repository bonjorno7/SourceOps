from . tools import num
import re


class TempCategory:
    """
    Temporarily holds the VMF categories when reading the .VMF file

    :param category: The category name
    :type category: :obj:`str`
    :param indent: The level of indentation (how far nested inside other classes)
    :type indent: :obj:`int`
    """

    # This class is used when reading the vmf file and when creating the vmf class later on
    def __init__(self, category, indent):
        self.category = category  # versioninfo, visgroups, world, solid, dispinfo, etc...
        self.indent = indent
        self.data = []  # Everything inside the curly brackets other than child categories (ex: "skyname" "sky_dust")
        self.children = []  # List of all children categories (ex: side, dispinfo, editor, etc...)
        self.current_child = None  # Used when going into nested children (ex: solid -> side -> dispinfo -> Normals)
        self.dic = {}  # This is where all the data is stored when it's cleaned, used when creating VMF class

    def __repr__(self):
        return self.category

    def add_line(self, line, indent):
        """
        :param line: The line of data to add to the current category
        :type line: :obj:`str`
        :param indent: The level of indentation (how far nested inside other classes)
        :type indent: :obj:`int`
        """
        diff = indent - self.indent  # Finding out how far into the nested children we need to go
        c = self
        for i in range(diff-1):
            c = c.current_child
        c.data.append(line)

    def add_child(self, category, indent):
        """
        :param category: The category name
        :type category: :obj:`str`
        :param indent: The level of indentation (how far nested inside other classes)
        :type indent: :obj:`int`
        """
        diff = indent - self.indent  # Same concept as self.add_line
        c = self
        for i in range(diff-1):
            c = c.current_child

        new_child = TempCategory(category, indent)
        c.children.append(new_child)
        c.current_child = new_child

    def clean_up(self):
        """
        Goes through all the data to remove unecessary characters
        """
        self.category = self.category.split()[0]  # We remove the tabs
        for i in self.data:
            clean = re.findall(r'\"(.*?)\"', i)  # We remove the double quotes and separate (example line: "id" "2688")
            self.dic[clean[0]] = num(clean[1])  # The values, IF possible are turned into either ints or floats

        for j in self.children:
            j.clean_up()  # Nested function calls


def file_parser(file):
    """
    Opens the file, extracts data line by line and turns it all into temporary categories

    :param file: The OS file to open, path needs to be included
    :type file: :obj:`str`
    :return: All the top level categories
    :rtype: :obj:`list` of :class:`TempCategory`
    """
    with open(file, "r") as vmf:

        indent = 0
        previous_line = "versioninfo\n"  # We only know it's a category the next line (the curly brackets open)
        extracted = []

        for line in vmf.readlines()[1:]:
            if "}" in line:
                indent -= 1
                if indent == 0:  # If indent is not 0 we know it's a child category and not a main category
                    extracted.append(t)
                continue

            if "{" in line:
                if indent > 0:  # If indent is not 0 we know it's a child category and not a main category
                    # Open curly brackets ALWAYS follow a category, so we know the previous line is the category name
                    t.add_child(previous_line, indent)
                else:
                    t = TempCategory(previous_line, indent)  # This is a main category (not a child category)
                indent += 1
                continue

            if "\"" in line: t.add_line(line, indent)  # ALL lines with data have double quotes in them

            previous_line = line

    for c in extracted:
        # clean_up is a recursive function we only need to call it on the main categories
        c.clean_up()

    return extracted  # This is used when creating a VMT class
