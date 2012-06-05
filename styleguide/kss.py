import re
from django.template import Template, Context
from docutils.core import publish_parts
from styleguide.models import StyleGuideSection


class KSSDocParser(object):
    """
    Converts a KSS-formatted text block into a StyleGuideSection.

    A full example::


        Heading Styles
        Styleguide 1.1

        A description for heading styles.

        .alt - An example of a modifier

        <h1 class="{{ modifier }}">Heading level 1</h1>
        <h2 class="{{ modifier }}">Heading level 2</h2>
        <h3 class="{{ modifier }}">Heading level 3</h3>


    This will be parsed into a title, description, modifiers,
    and a sample template, separated by double newlines.

    The position in the style guide is determined by the
    Styleguide declaration.
    """

    styleguide_position_re = re.compile(r"Styleguide (\S+)")
    leading_spaces_re = re.compile(r"^\s*")

    def __init__(self, content):
        self.content = content

    def is_valid_section(self):
        """
        :return: bool True if content can be parsed
        """
        return bool(self.styleguide_position_re.search(self.content))

    def parse_section(self):
        """
        :return: StyleGuideSection from parsing content
        """

        blocks = self._trim_leading_spaces(self.content).strip().split("\n\n")

        blocks, position = self._parse_position(blocks)
        blocks, raw_template, template = self._parse_template(blocks)
        blocks, modifiers = self._parse_modifiers(blocks, raw_template)
        blocks, title = self._parse_title(blocks)
        blocks, desc = self._parse_desc(blocks)

        return StyleGuideSection(
            position=position,
            title=title,
            desc=desc,
            modifiers=modifiers,
            template=template,
        )

    def _parse_position(self, blocks):
        position = None
        out = []
        lines = "\n\n".join(blocks).split("\n")
        for line in lines:
            result = self.styleguide_position_re.search(line)
            if result:
                position = result.group(1)
            else:
                out.append(line)
        return "\n".join(out).split("\n\n"), position

    def _parse_modifiers(self, blocks, raw_template):
        modifiers = []
        modifier_block = None
        out = []
        for block in blocks:
            if " - " in block and not modifier_block:
                modifier_block = block
            else:
                out.append(block)

        last_indent = None
        if modifier_block:
            for line in modifier_block.split("\n"):
                indent = self._get_indent(line)
                if last_indent and indent > last_indent:
                    modifiers[-1]['description'] += line
                elif " - " in line:
                    modifier, desc = line.split(" - ")
                    modifier_template = None
                    if raw_template is not None:
                        modifier_class = modifier.lstrip(".")
                        modifier_template = self._render_template(
                            raw_template, {
                                'modifier': modifier_class,
                            })
                    modifiers.append({
                        'modifier': modifier,
                        'description': desc,
                        'template': modifier_template,
                    })
                    last_indent = indent
                else:
                    last_indent = None

        return out, modifiers

    def _parse_template(self, blocks):
        raw_template = None
        template = None
        out = []
        raw_template_blocks = []
        for block in blocks:
            if block.strip().startswith("<") or raw_template_blocks:
                raw_template_blocks.append(self._trim_leading_spaces(block))
            else:
                out.append(block)
        raw_template = "\n\n".join(raw_template_blocks)
        template = self._render_template(raw_template, { 'modifier': '' })
        return out, raw_template, template

    def _parse_title(self, blocks):
        return blocks[1:], blocks[0].strip()

    def _parse_desc(self, blocks):

        desc_source = "\n\n".join(blocks)
        return [], self._parse_restructuredtext(desc_source)

    def _parse_restructuredtext(self, source):
        parts = publish_parts(
            source=source,
            parser_name='restructuredtext',
            settings_overrides={'file_insertion_enabled': 0, 'raw_enabled': 0},
            writer_name='html')
        return parts['body']

    def _get_indent(self, line):
        return len(self.leading_spaces_re.search(line).group(0))

    def _render_template(self, template_string, vars):
        tpl = Template(template_string)
        context = Context(vars)
        return tpl.render(context)

    def _trim_leading_spaces(self, text):
        lines = text.split("\n")
        max_indent = 9999
        for line in lines:
            if line.strip():
                max_indent = min(self._get_indent(line), max_indent)
        out = []
        for line in lines:
            if line.strip():
                out.append(line[max_indent:])
            else:
                out.append("")
        return "\n".join(out)



