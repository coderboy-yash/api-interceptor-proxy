import xml.etree.ElementTree as ET

def extract_unique_tags(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    tags = set()

    for elem in root.iter():
        # Remove namespace if present
        tag = elem.tag.split('}')[-1]
        tags.add(tag)

    return tags


if __name__ == "__main__":
    xml_path = "traffic1.xml"   # change this
    unique_tags = extract_unique_tags(xml_path)

    for tag in sorted(unique_tags):
        print(tag)
