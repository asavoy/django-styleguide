from styleguide.models import StyleGuide
from styleguide.kss import KSSDocParser



class StyleGuideBuilder(object):
    """
    Builds a StyleGuide from a collection of KSS-formatted
    doc comments.
    """

    def __init__(self, comment_collector):
        self.comment_collector = comment_collector

    def get_style_guide(self):
        # find all comment blocks
        comments_list = self.comment_collector.get_comments_list()

        # parse into StyleGuideSection
        sections = []
        for raw_section in comments_list:
            parser = KSSDocParser(raw_section)
            if parser.is_valid_section():
                sections.append(parser.parse_section())

        # order by position
        sections = sorted(sections, key=lambda section: section.comparable_position())

        # put together the StyleGuide instance
        guide = StyleGuide("Style Guide", sections)
        return guide


