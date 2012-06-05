import logging
import os
from django.conf import settings
from styleguide.scss import SCSSCommentParser

logger = logging.getLogger(__name__)

FILE_COLLECTOR_ROOT = getattr(settings, 'STYLEGUIDE_FILE_COLLECTOR_ROOT',
                              getattr(settings, 'STATIC_ROOT'))
FILE_COLLECTOR_EXTS = getattr(settings, 'STYLEGUIDE_FILE_COLLECTOR_EXTS',
                              ('.css', '.less', '.sass', '.scss'))


class CommentCollector(object):

    def get_comments_list(self):
        """
        Returns a list of comment blocks.
        :return: list containing strings
        """

        raise NotImplemented("Subclasses required to implement")



class ExampleCollector(CommentCollector):
    """
    Returns some sample comment blocks, for testing purposes.
    """

    def get_comments_list(self):
        return [
            """
            Example style guide

            Styleguide 1
            """,
            """
            Typography

            Common text styles and line-heights.

            Styleguide 1.1
            """,
            """
            Headings

            .alt - Use alternate variation

            Styleguide 1.2
            """,
            """
            Lists

            By default, lists receive no styling.

            .plain - Add plain styling
            .fancy - Add image bullets

                <ul class="{{ modifier }}">
                    <li>Item 1</li>
                    <li>Item 2</li>
                    <li>Item 3</li>
                </ul>

            Styleguide 1.3
            """,
        ]



class FileCollector(CommentCollector):
    """
    Collects comment blocks from files that match a file search.
    """

    def filename_is_match(self, filename):
        return any(filename.endswith(ext) for ext in FILE_COLLECTOR_EXTS)

    def iterate_matching_files(self):
        for root, dirs, files in os.walk(FILE_COLLECTOR_ROOT):
            for f in files:
                if self.filename_is_match(f):
                    yield os.path.join(root, f)

    def get_comments_list(self):
        out = []
        for filepath in self.iterate_matching_files():
            src_file = open(filepath, 'r')
            contents = src_file.read()
            name = os.path.basename(filepath)
            src_file.close()
            parser = SCSSCommentParser(contents, name)
            blocks = parser.blocks()
            out.extend(blocks)
            logger.debug("%s: Found %d comment blocks"
                         % (filepath, len(blocks)))

        return out
