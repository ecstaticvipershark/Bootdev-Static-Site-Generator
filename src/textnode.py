from enum import Enum
from typing import Type

from htmlnode import LeafNode
import re
import sys

class TextType(Enum):
    TEXT = "plain"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode():
    def __init__(self, text, Text_Type: TextType, url=None):
        self.text = text
        self.text_type = Text_Type
        self.url = url

    def __eq__(self, other) -> bool:
        return self.text == other.text and self.text_type == other.text_type and self.url == other.url

    def __repr__(self) -> str:
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"



def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    text = text_node.text
    url = text_node.url
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text, {"href": url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": url, "alt": text})
    else:
        raise ValueError(f"Unknown text type: {text_node.text_type}")

# Converts raw markdown strings into a list of text nodes matching their types according to delimeters
def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    new_list = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_list.append(old_node)
            continue
        split_node = old_node.text.split(delimiter)
        if len(split_node) % 2 == 0:
            raise Exception("unclosed delimiter")
        for i in range(len(split_node)):
            if split_node[i] == "":
                continue
            elif i % 2 == 0:
                new_list.append(TextNode(split_node[i], TextType.TEXT))
            else:
                new_list.append(TextNode(split_node[i], text_type))
    return new_list

#Converts raw markdown strings that have images in them into a list of text and image text nodes
def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_list = []
    for old_node in old_nodes:
        images = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", old_node.text)
        if not images:
                new_list.append(old_node)
                continue
        text_and_images = re.split(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", old_node.text)
        for i, chunk in enumerate(text_and_images):
            if i % 3 == 0:
                if chunk != "":
                    new_list.append(TextNode(chunk, TextType.TEXT))
            elif i % 3 == 1:
                continue
            else:
                new_list.append(TextNode(text_and_images[i-1], TextType.IMAGE, chunk))
    return new_list


#Converts raw markdown strings that contain non image links into lists of text and link text nodes
def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_list = []
    for old_node in old_nodes:
        links = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", old_node.text)
        if not links:
            new_list.append(old_node)
            continue
        text_and_links = re.split(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", old_node.text)
        for i, chunk in enumerate(text_and_links):
            if i % 3 == 0:
                if chunk != "":
                    new_list.append(TextNode(chunk, TextType.TEXT))
            elif i % 3 == 1:
                continue
            else:
                new_list.append(TextNode(text_and_links[i-1], TextType.LINK, chunk))
    return new_list



# Converts markdown strings into inline text nodes matching their type using the above functions as helpers.
# It can handle: bold, itaclic, code, plain text, image links and non image links
def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = TextNode(text, TextType.TEXT)
    nodes = split_nodes_delimiter([nodes], "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

#Takes a raw markdown string representing a full document and splits it into a list of block strings based on two new lines
def markdown_to_blocks(markdown: str) -> list[str]:
    if not markdown:
        raise Exception("Input must not be empty")
    split_strings = markdown.split("\n\n")
    stripped_strings = []
    for string in split_strings:
        stripped = string.strip()
        if stripped:
            stripped_strings.append(stripped.strip())
    return stripped_strings

#Takes a single block of markdown text as input and returns the BlockType
class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unorderes_list"
    ORDERED_LIST = "ordered_list"


def block_to_block_type(markdown: str) -> BlockType:
    if re.match(r"^#{1,6} ", markdown):
        return BlockType.HEADING
    if re.match("^`{3}\n", markdown) and re.search("\n`{3}$", markdown):
        return BlockType.CODE
    if all(re.match(r"^>.+", line) for line in markdown.split("\n")):
        return BlockType.QUOTE
    if all(re.match(r"^- ", line) for line in markdown.split("\n")):
        return BlockType.UNORDERED_LIST
    lines = markdown.split("\n")
    for i, line in enumerate(lines, 1):
        if not line.startswith(f"{i}. "):
            return BlockType.PARAGRAPH
    return BlockType.ORDERED_LIST
