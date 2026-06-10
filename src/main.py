from textnode import TextNode, TextType

def main():
    node = TextNode("This is a picture of a rabbit", TextType.IMAGE, "https://www.baltana.com/files/wallpapers-6/Cute-White-Baby-Rabbit-Wallpaper-19291.jpg")
    print(node)

main()
