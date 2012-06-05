# Attribution note:
# This code almost directly ported from:
# https://github.com/kneath/kss/blob/master/lib/kss/comment_parser.rb

import re


class SCSSCommentParser(object):

    def __init__(self, source, name=None):
        self.name = name if name is not None else "<not specified>"
        self.source = source
        self._blocks = None

    _single_line_comment_re = re.compile(r"^\s*//")
    def is_single_line_comment(self, line):
        return bool(self._single_line_comment_re.match(line))

    _start_multi_line_comment_re = re.compile(r"^\s*/\*")
    def is_start_multi_line_comment(self, line):
        return bool(self._start_multi_line_comment_re.match(line))

    _end_multi_line_comment_re = re.compile(r".*\*/")
    def is_end_multi_line_comment(self, line):
        return bool(self._end_multi_line_comment_re.match(line))

    _parse_single_line_clean_re = re.compile(r"\s*//")
    def parse_single_line(self, line):
        cleaned = self._parse_single_line_clean_re.sub("", line).rstrip()
        return cleaned

    _parse_multi_line_clean_start_re = re.compile(r"\s*/\*")
    _parse_multi_line_clean_end_re = re.compile(r"\*/")
    def parse_multi_line(self, line):
        cleaned = self._parse_multi_line_clean_start_re.sub("", line)
        cleaned = self._parse_multi_line_clean_end_re.sub("", cleaned).rstrip()
        return cleaned

    def preserve_whitespace(self):
        return False

    def blocks(self):
        if self._blocks is None:
            self._blocks = self.parse_blocks()
        return self._blocks

    def parse_blocks(self):

        current_block = ""
        inside_single_line_block = False
        inside_multi_line_block  = False
        blocks = []
        lines = self.source.split("\n")
        for line in lines:
            # Parse single-line style
            if self.is_single_line_comment(line):
                parsed = self.parse_single_line(line)
                if inside_single_line_block:
                    current_block += "\n%s" % parsed
                else:
                    current_block = unicode(parsed)
                    inside_single_line_block = True

            # Parse multi-lines style
            if self.is_start_multi_line_comment(line) or inside_multi_line_block:
                parsed = self.parse_multi_line(line)
                if inside_multi_line_block:
                    current_block += "\n%s" % parsed
                else:
                    current_block = parsed
                    inside_multi_line_block = True

            # End a multi-line block if detected
            if self.is_end_multi_line_comment(line):
                inside_multi_line_block = False

            # Store the current block if we're done
            if not(self.is_single_line_comment(line) or inside_multi_line_block):
                if current_block:
                    blocks.append(self.normalize(current_block))
                inside_single_line_block = False
                current_block = ""

        return blocks

    def normalize(self, text_block):

        # Strip out any preceding [whitespace]* that occur on every line. Not
        # the smartest, but I wonder if I care.
        check_preceding_re = re.compile(r"^(\s*\*+)")
        strip_all_preceding_re = re.compile(r"^(\s*\*+)", flags=re.MULTILINE)
        if check_preceding_re.search(text_block):
            text_block = strip_all_preceding_re.sub("", text_block)

        # Strip consistent indenting by measuring first line's whitespace
        indent_size = None
        lines = text_block.split("\n")
        unindented = []
        preceding_whitespace_re = re.compile(r"^\s*")
        for line in lines:
            preceding_whitespace = len(preceding_whitespace_re.search(line).group(0))
            if indent_size is None and line.strip() != "":
                indent_size = preceding_whitespace
            if line == "":
                line = ""
            elif (indent_size <= preceding_whitespace) and (indent_size > 0):
                line = line[indent_size:]
            unindented.append(line)

        return "\n".join(unindented).strip()

