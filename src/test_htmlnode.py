import unittest
from unittest.loader import VALID_MODULE_NAME
from htmlnode import HTMLNode, LeafNode, ParentNode
import htmlnode
from textnode import TextNode, text_node_to_html_node, TextType, split_nodes_delimiter

class TestHTMLNode(unittest.TestCase):

# Basic htmlnode test

    def test_repr(self):
        node = HTMLNode("h1", "Test Header", None, {"cols": "11"})
        self.assertEqual(node.__repr__(), "h1, Test Header, children: None, {'cols': '11'}")
    def test_props_to_html(self):
        node = HTMLNode("h1", "Test Header", None, {"cols": "11"})
        self.assertEqual(node.props_to_html(), ' cols="11"')

    def test_props_to_html2(self):
        node = HTMLNode("h1", "Test Header", None, {"cols": "11"})
        node2 = HTMLNode("p", "Paragraph text test", [node], {"autocapitalize": "None", "data-*": "None"})
        self.assertEqual(node2.props_to_html(), ' autocapitalize="None" data-*="None"')

    def test_props_to_html3(self):
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), '')

# Leaf to html test

    def test_leaf_to_html(self):
        leaf = LeafNode("p", "This is a paragraph of text.")
        self.assertEqual(leaf.to_html(), "<p>This is a paragraph of text.</p>")

    def test_leaf_to_html2(self):
        leaf = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(leaf.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_leaf_to_html3(self):
        leaf = LeafNode("img", None, {"src": "rabbit.png"})
        self.assertRaises(ValueError, leaf.to_html)

    def test_leaf_to_html4(self):
        leaf = LeafNode("img", "", {"src": "rabbit.png"})
        self.assertEqual(leaf.to_html(), '<img src="rabbit.png"></img>')

# Parent to html tests
    
    def test_parent_node_tag_error(self):
        parent1 = ParentNode(None, [LeafNode("img", "", {"src": "rabbit.png"})])  # type: ignore
        self.assertRaises(ValueError, parent1.to_html)

    def test_parent_node_childless_error(self):
        parent1 = ParentNode("p", None, {"class": "primary-button"})  # type: ignore
        self.assertRaises(ValueError, parent1.to_html)

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with__mult_children(self):
        child_node1 = LeafNode("span", "child")
        child_node2 = LeafNode("a", "https://google.com")
        parent_node = ParentNode("div", [child_node1, child_node2])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span><a>https://google.com</a></div>")

# Text node to html leaf node

    def test_text_to_leaf(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_link_text_to_leaf(self):
        node = TextNode("Link to Google", TextType.LINK, "https://www.google.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Link to Google")
        self.assertEqual(html_node.props, {"href": "https://www.google.com"})

    def test_bold_text_to_leaf(self):
        node = TextNode("Bold text test", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text test")

    def test_italic_text_to_leaf(self):
        node = TextNode("Italic text test", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text test")

    def test_code_text_to_leaf(self):
        node = TextNode("print('hi')", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "print('hi')")

    def test_image_text_to_leaf(self):
        node = TextNode("Alt text", TextType.IMAGE, "https://example.com/img.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "https://example.com/img.png", "alt": "Alt text"})

# split_nodes_delimiter tests

    def test_code_block_backtick(self):
        nodes = [TextNode("print `x = 1` end", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual([(n.text, n.text_type) for n in result],
        [("print ", TextType.TEXT), ("x = 1", TextType.CODE), (" end", TextType.TEXT)])

    def test_bold_double_asterisk(self):
        nodes = [TextNode("a **bold** b", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual([(n.text, n.text_type) for n in result],
        [("a ", TextType.TEXT), ("bold", TextType.BOLD), (" b", TextType.TEXT)])

    def test_italic_underscore(self):
        nodes = [TextNode("before _italics_ after", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        self.assertEqual([(n.text, n.text_type) for n in result],
        [("before ", TextType.TEXT), ("italics", TextType.ITALIC), (" after", TextType.TEXT)])

    def test_non_text_node_passthrough(self):
        nodes = [TextNode("link text", TextType.LINK, "https://ex.com"), TextNode("x _y_ z", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
# first node unchanged, second split
        self.assertEqual(result[0].text_type, TextType.LINK)
        self.assertEqual([(n.text, n.text_type) for n in result[1:]],
        [("x ", TextType.TEXT), ("y", TextType.ITALIC), (" z", TextType.TEXT)])

    def test_starts_with_delimiter_empty_segment(self):
        nodes = [TextNode("_lead_", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        self.assertEqual([(n.text, n.text_type) for n in result],
        [("lead", TextType.ITALIC)])

    def test_unclosed_delimiter_raises(self):
        nodes = [TextNode("open `code block", TextType.TEXT)]
        with self.assertRaises(Exception):
            split_nodes_delimiter(nodes, "`", TextType.CODE)

if __name__ == "__main__":
    unittest.main()
