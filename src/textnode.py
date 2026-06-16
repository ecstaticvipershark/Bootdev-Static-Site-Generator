from enum import Enum

from htmlnode import LeafNode
import re

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



def extract_md_images(text: str) -> list[tuple]:
    matches = re.findall(r"!\[(.+?)\]\((.+?)\)", text)
    return matches

def extract_md_links(text: str) -> list[tuple]:
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches


def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = TextNode(text, TextType.TEXT)
    nodes = split_nodes_delimiter([nodes], "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes
