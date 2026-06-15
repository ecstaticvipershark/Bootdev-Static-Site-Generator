class HTMLNode:
    def __init__(self, tag: str | None = None, value: str | None = None, children: list["HTMLNode"] | None = None, props: dict | None = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        result = ""
        if self.props:
            for attr in self.props:
                result += f' {attr}="{self.props[attr]}"'
        return result

    def __repr__(self) -> str:
        return f"{self.tag}, {self.value}, children: {self.children}, {self.props}"

class LeafNode(HTMLNode):
    def __init__(self, tag: str | None, value: str | None, props: dict | None = None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value is None:
            raise ValueError
        if self.tag is None:
            return f"{self.value}"
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self) -> str:
        return f"{self.tag}, {self.value}, {self.props})" 

class ParentNode(HTMLNode):
    def __init__(self, tag: str, children: list["HTMLNode"], props: dict | None = None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("Tag must be provided")
        if self.children is None:
            raise ValueError("Children must be provided")
        children_str = ""
        for child in self.children:
            children_str += child.to_html()
        return f'<{self.tag}{self.props_to_html()}>{children_str}</{self.tag}>'
