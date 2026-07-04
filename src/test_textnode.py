from typing import Self
import unittest
from textnode import TextNode, TextType, text_node_to_html_node, split_nodes_delimiter, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type, BlockType

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = TextNode("This is a text node", TextType.ITALIC, "https://www.google.com")
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_eq_two(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.TEXT)
        self.assertEqual(node2, node)


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


# Split Image Nodes
        
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],new_nodes,)

    def test_split_images_no_image(self):
        node = TextNode("This string contains no images at all", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([TextNode("This string contains no images at all", TextType.TEXT)], new_nodes)

    def test_split_image_at_start(self):
        node = TextNode("![Start image](rabbit.png) there should be an image node before this text node", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([TextNode("Start image", TextType.IMAGE, "rabbit.png"),
                              TextNode(" there should be an image node before this text node", TextType.TEXT)],
            new_nodes
            )

    def test_split_images_bold(self):
        node = TextNode("This TextType is BOLD instead of TEXT", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([TextNode("This TextType is BOLD instead of TEXT", TextType.BOLD)], new_nodes)

    def test_split_images_multi_node(self):
        node1 = TextNode("![Start image](rabbit.png) there should be an image node before this text node", TextType.TEXT)
        node2 = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node1, node2])
        self.assertListEqual([TextNode("Start image", TextType.IMAGE, "rabbit.png"),
                TextNode(" there should be an image node before this text node", TextType.TEXT),
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),],
            new_nodes)

# Split Link Nodes

    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://www.google.com) and another [second link](https://www.boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.google.com"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second link", TextType.LINK, "https://www.boot.dev"),
            ],new_nodes,)

    def test_split_links_no_link(self):
        node = TextNode("This string contains no links at all", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([TextNode("This string contains no links at all", TextType.TEXT)], new_nodes)

    def test_split_link_at_start(self):
        node = TextNode("[Start link](https://www.google.com) there should be a link node before this text node", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([TextNode("Start link", TextType.LINK, "https://www.google.com"),
                            TextNode(" there should be a link node before this text node", TextType.TEXT)],
            new_nodes
            )

    def test_split_links_bold(self):
        node = TextNode("This TextType is BOLD instead of TEXT", TextType.BOLD)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([TextNode("This TextType is BOLD instead of TEXT", TextType.BOLD)], new_nodes)

    def test_split_links_multi_node(self):
        node1 = TextNode("[Start link](https://www.google.com) there should be a link node before this text node", TextType.TEXT)
        node2 = TextNode(
            "This is text with a [link](https://www.google.com) and another [second link](https://www.boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node1, node2])
        self.assertListEqual([TextNode("Start link", TextType.LINK, "https://www.google.com"),
                TextNode(" there should be a link node before this text node", TextType.TEXT),
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.google.com"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second link", TextType.LINK, "https://www.boot.dev"),],
            new_nodes)

# Text To Text Nodes 

    def test_text_to_text_nodes(self):
        results = text_to_textnodes("This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")
        self.assertListEqual([
    TextNode("This is ", TextType.TEXT),
    TextNode("text", TextType.BOLD),
    TextNode(" with an ", TextType.TEXT),
    TextNode("italic", TextType.ITALIC),
    TextNode(" word and a ", TextType.TEXT),
    TextNode("code block", TextType.CODE),
    TextNode(" and an ", TextType.TEXT),
    TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
    TextNode(" and a ", TextType.TEXT),
    TextNode("link", TextType.LINK, "https://boot.dev"),
], results)

    def test_text_to_textnodes_plain(self):
        nodes = text_to_textnodes("Just plain text")
        self.assertListEqual([TextNode("Just plain text", TextType.TEXT)], nodes)

    def test_text_to_textnodes_bold(self):
        nodes = text_to_textnodes("**bold**")
        self.assertListEqual([TextNode("bold", TextType.BOLD)], nodes)

    def test_text_to_textnodes_italic(self):
        nodes = text_to_textnodes("_italic_")
        self.assertListEqual([TextNode("italic", TextType.ITALIC)], nodes)

    def test_text_to_textnodes_code(self):
        nodes = text_to_textnodes("`code`")
        self.assertListEqual([TextNode("code", TextType.CODE)], nodes)

    def test_text_to_textnodes_image(self):
        nodes = text_to_textnodes("![rabbit](rabbit.png)")
        self.assertListEqual([TextNode("rabbit", TextType.IMAGE, "rabbit.png")], nodes)

    def test_text_to_textnodes_link(self):
        nodes = text_to_textnodes("[click me](https://www.google.com)")
        self.assertListEqual([TextNode("click me", TextType.LINK, "https://www.google.com")], nodes)

#Markdown to blocks test
    def test_markdown_to_blocks(self):
        blocks = markdown_to_blocks("""# This is a heading

This is a paragraph of text. It has some **bold** and _italic_ words inside of it.

- This is the first list item in a list block
- This is a list item
- This is another list item""")
        self.assertListEqual(blocks, ['# This is a heading', 'This is a paragraph of text. It has some **bold** and _italic_ words inside of it.',
                                      '- This is the first list item in a list block\n- This is a list item\n- This is another list item'])

    def test_markdown_to_blocks_extra_blank_lines(self):
        blocks = markdown_to_blocks("block one\n\n\n\nblock two")
        self.assertListEqual(blocks, ["block one", "block two"])

    def test_markdown_to_blocks_strips_whitespace(self):
        blocks = markdown_to_blocks("  block one  \n\n  block two  ")
        self.assertListEqual(blocks, ["block one", "block two"])

    def test_markdown_to_blocks_single_block(self):
        blocks = markdown_to_blocks("just one block here")
        self.assertListEqual(blocks, ["just one block here"])

    def test_markdown_to_blocks_empty_string(self):
        with self.assertRaises(Exception):
            markdown_to_blocks("")

#takes a single block of markdown text as input and returns the BlockType

    def test_block_to_block_type_heading(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)

    def test_block_to_block_type_heading_max(self):
        self.assertEqual(block_to_block_type("###### Heading"), BlockType.HEADING)

    def test_block_to_block_type_heading_too_many(self):
        self.assertEqual(block_to_block_type("####### Heading"), BlockType.PARAGRAPH)

    def test_block_to_block_type_code(self):
        self.assertEqual(block_to_block_type("```\nsome code\n```"), BlockType.CODE)

    def test_block_to_block_type_quote(self):
        self.assertEqual(block_to_block_type(">quote\n>another quote"), BlockType.QUOTE)

    def test_block_to_block_type_unordered_list(self):
        self.assertEqual(block_to_block_type("- item one\n- item two"), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_ordered_list(self):
        self.assertEqual(block_to_block_type("1. item one\n2. item two\n3. item three"), BlockType.ORDERED_LIST)

    def test_block_to_block_type_ordered_list_wrong_order(self):
        self.assertEqual(block_to_block_type("1. item one\n3. item three"), BlockType.PARAGRAPH)

    def test_block_to_block_type_paragraph(self):
        self.assertEqual(block_to_block_type("just a normal paragraph"), BlockType.PARAGRAPH)

    def test_block_to_block_type_empty(self):
        self.assertEqual(block_to_block_type(""), BlockType.PARAGRAPH)

    def test_block_to_block_type_quote_partial(self):
        self.assertEqual(block_to_block_type(">quote\nnot a quote"), BlockType.PARAGRAPH)

    def test_block_to_block_type_unordered_list_partial(self):
        self.assertEqual(block_to_block_type("- item one\nnot a list item"), BlockType.PARAGRAPH)

    def test_block_to_block_type_whitespace_only(self):
        self.assertEqual(block_to_block_type("   "), BlockType.PARAGRAPH)

if __name__ == "__main__":
    unittest.main()
