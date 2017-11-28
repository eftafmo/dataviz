import os
import xml.etree.ElementTree as ET


schema_path = input('XML schema path: ')

if not os.path.exists(schema_path):
    print('File path incorrect!')
else:
    with open(schema_path, 'r') as file:
        tree = ET.parse(file)
        schema = tree.getroot()

        fields = schema.findall('field')
        fields.sort(key=lambda x: x.attrib['name'])

        for i in range(len(fields)):
            schema.remove(fields[i])
            schema.insert(i, fields[i])

        text_en_type = schema.find("fieldType[@name='text_en']")
        ascii_filter = ET.fromstring(
            "<filter class=\"solr.ASCIIFoldingFilterFactory\" "
            "preserveOriginal=\"true\"/>"
        )
        for analyzer in text_en_type.findall('analyzer'):
            analyzer.insert(0, ascii_filter)

        tree.write(schema_path, xml_declaration=True)
