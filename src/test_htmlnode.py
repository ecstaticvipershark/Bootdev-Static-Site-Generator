import unittest
from unittest.loader import VALID_MODULE_NAME
from htmlnode import HTMLNode, LeafNode, ParentNode
import htmlnode

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

    def test_to_html_with_mult_children(self):
        child_node1 = LeafNode("span", "child")
        child_node2 = LeafNode("a", "https://google.com")
        parent_node = ParentNode("div", [child_node1, child_node2])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span><a>https://google.com</a></div>")


if __name__ == "__main__":
    unittest.main()
