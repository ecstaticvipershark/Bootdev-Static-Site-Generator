from typing import Self
import unittest
from textnode import TextNode, TextType, text_node_to_html_node, split_nodes_delimiter, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type, BlockType, markdown_to_html_node

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


# takes a full markdown document and converts it to a full tree starting with an html div node going all the way down to leaf nodes

    def test_paragraph(self):
        md = "This is a paragraph of text."
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is a paragraph of text.</p></div>",
        )

    def test_paragraph_multiline_joins_with_space(self):
        md = "This is line one\nand this is line two."
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is line one and this is line two.</p></div>",
        )

    def test_multiple_paragraphs(self):
        md = "Paragraph one.\n\nParagraph two."
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>Paragraph one.</p><p>Paragraph two.</p></div>",
        )

    def test_heading_h1(self):
        md = "# Heading one"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Heading one</h1></div>",
        )

    def test_heading_h3(self):
        md = "### Heading three"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h3>Heading three</h3></div>",
        )

    def test_heading_then_paragraph(self):
        md = "# Title\n\nSome body text here."
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Title</h1><p>Some body text here.</p></div>",
        )

    def test_paragraph_with_inline_bold(self):
        md = "This has **bold** text."
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This has <b>bold</b> text.</p></div>",
        )

    def test_code_block(self):
        md = "```\nprint('hello')\n```"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>print('hello')\n</code></pre></div>",
        )

    def test_code_block_multiline(self):
        md = "```\nline one\nline two\n```"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>line one\nline two\n</code></pre></div>",
        )

    def test_code_block_preserves_inline_markdown_as_literal(self):
        md = "```\n**not bold**\n```"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>**not bold**\n</code></pre></div>",
        )

    def test_code_block_then_paragraph(self):
        md = "```\ncode here\n```\n\nA normal paragraph."
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>code here\n</code></pre><p>A normal paragraph.</p></div>",
        )

    def test_code_block_empty(self):
        md = "```\n```"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code></code></pre></div>",
        )

    def test_heading_h6_valid(self):
        md = "###### Heading six"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h6>Heading six</h6></div>",
        )

    def test_heading_seven_hashes_produces_invalid_tag(self):
        # markdown doesn't support h7 — block_to_block_type correctly
        # rejects 7+ hashes and falls back to PARAGRAPH.
        md = "####### Seven hashes"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>####### Seven hashes</p></div>",
        )

    def test_heading_no_space_treated_as_paragraph(self):
        md = "#Title"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>#Title</p></div>",
        )

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_blockquote_simple(self):
        md = "> This is a quote"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a quote</blockquote></div>",
        )

    def test_blockquote_multiline(self):
        md = "> line one\n> line two"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>line one\nline two</blockquote></div>",
        )

    def test_blockquote_no_space_after_marker(self):
        md = ">no space here"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>no space here</blockquote></div>",
        )

    def test_blockquote_with_inline_bold(self):
        md = "> This is **bold** in a quote"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is <b>bold</b> in a quote</blockquote></div>",
        )

    def test_blockquote_with_inline_italic_and_code(self):
        md = "> some _italic_ and `code` words"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>some <i>italic</i> and <code>code</code> words</blockquote></div>",
        )

    def test_blockquote_then_paragraph(self):
        md = "> A quote here\n\nA normal paragraph."
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>A quote here</blockquote><p>A normal paragraph.</p></div>",
        )

    def test_blockquote_multiline_three_lines(self):
        md = "> line one\n> line two\n> line three"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>line one\nline two\nline three</blockquote></div>",
        )


    def test_unordered_list_simple(self):
        md = "- item one\n- item two\n- item three"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>item one</li><li>item two</li><li>item three</li></ul></div>",
        )

    def test_unordered_list_single_item(self):
        md = "- only item"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>only item</li></ul></div>",
        )

    def test_unordered_list_with_inline_formatting(self):
        md = "- **bold** item\n- _italic_ item\n- `code` item"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li><b>bold</b> item</li><li><i>italic</i> item</li><li><code>code</code> item</li></ul></div>",
        )

    def test_unordered_list_then_paragraph(self):
        md = "- item one\n- item two\n\nA paragraph after."
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>item one</li><li>item two</li></ul><p>A paragraph after.</p></div>",
        )

    def test_ordered_list_simple(self):
        md = "1. first\n2. second\n3. third"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>first</li><li>second</li><li>third</li></ol></div>",
        )

    def test_ordered_list_single_item(self):
        md = "1. only item"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>only item</li></ol></div>",
        )

    def test_ordered_list_with_inline_formatting(self):
        md = "1. **bold** first\n2. _italic_ second\n3. `code` third"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li><b>bold</b> first</li><li><i>italic</i> second</li><li><code>code</code> third</li></ol></div>",
        )

    def test_ordered_list_then_paragraph(self):
        md = "1. first\n2. second\n\nA paragraph after."
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>first</li><li>second</li></ol><p>A paragraph after.</p></div>",
        )

    def test_ordered_list_double_digit_items(self):
        md = "\n".join(f"{i}. item {i}" for i in range(1, 11))
        node = markdown_to_html_node(md)
        html = node.to_html()
        expected_items = "".join(f"<li>item {i}</li>" for i in range(1, 11))
        self.assertEqual(
            html,
            f"<div><ol>{expected_items}</ol></div>",
        )

if __name__ == "__main__":
    unittest.main()
