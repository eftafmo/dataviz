import os
import lxml.etree as ElementTree

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Adds ASCIIFoldingFilterFactory to schema.xml and reorders fields'

    def add_arguments(self, parser):
        parser.add_argument('schema_path', help="the Solr schema file")

    def handle(self, *args, **options):
        schema_path = options['schema_path']
        if not os.path.exists(schema_path):
            raise CommandError('Cannot open file "%s".' % schema_path)
        with open(schema_path, 'r') as file:
            tree = ElementTree.parse(file)
            schema = tree.getroot()

            fields = schema.findall('field')
            fields.sort(key=lambda x: x.attrib['name'])

            for i in range(len(fields)):
                schema.remove(fields[i])
                schema.insert(i, fields[i])

            text_en_type = schema.find("fieldType[@name='text_en']")
            for analyzer in text_en_type.findall('analyzer'):
                ascii_filter = ElementTree.fromstring(
                    "<filter class=\"solr.ASCIIFoldingFilterFactory\" "
                    "preserveOriginal=\"true\"/>"
                )
                analyzer.insert(0, ascii_filter)

            tree.write(schema_path, xml_declaration=True, encoding="UTF-8")
