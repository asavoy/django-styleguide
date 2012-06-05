from django.test import TestCase
from styleguide.scss import SCSSCommentParser
from styleguide.models import StyleGuideSection
from styleguide.kss import KSSDocParser


class KSSDocParserTest(TestCase):

    def test_empty_comment(self):

        parser = KSSDocParser("")
        self.assertFalse(parser.is_valid_section())

    def test_minimmum_comment(self):

        parser = KSSDocParser("""
            Styleguide 1
        """)
        self.assertTrue(parser.is_valid_section())

        section = parser.parse_section()
        self.assertEquals(section.position, '1')

    def test_title_comment(self):

        parser = KSSDocParser("""
            Style guide section title
            Styleguide 1.1
        """)
        self.assertTrue(parser.is_valid_section())

        section = parser.parse_section()
        self.assertEquals(section.title, 'Style guide section title')
        self.assertEquals(section.position, '1.1')


    def test_descriptive_comment(self):

        parser = KSSDocParser("""
            Style guide section title

            Description here.

            More description.

            Styleguide 1.1
        """)
        self.assertTrue(parser.is_valid_section())

        section = parser.parse_section()
        self.assertEquals(section.title, 'Style guide section title')
        self.assertEquals(section.desc, 'Description here.\n\nMore description.\n')
        self.assertEquals(section.position, '1.1')


    def test_modifiers_comment(self):

        parser = KSSDocParser("""
            Style guide section title

            .emphasis - Adds brighter highlight.
            .subtle - Use for secondary actions.

            Styleguide 1.1
        """)
        self.assertTrue(parser.is_valid_section())

        section = parser.parse_section()
        self.assertEquals(section.title, 'Style guide section title')
        self.assertEquals(section.modifiers,
                          [{'description': 'Adds brighter highlight.',
                            'modifier': '.emphasis',
                            'template': None},
                           {'description': 'Use for secondary actions.',
                            'modifier': '.subtle',
                            'template': None}])
        self.assertEquals(section.position, '1.1')


    def test_comment_with_template(self):

        parser = KSSDocParser("""
            Style guide section title

              <p>
                The quick brown fox...
              </p>

            Styleguide 1.1
        """)
        self.assertTrue(parser.is_valid_section())

        section = parser.parse_section()
        self.assertEquals(section.title, 'Style guide section title')
        self.assertEquals(section.template, '<p>\n  The quick brown fox...\n</p>\n')
        self.assertEquals(section.position, '1.1')


    def test_modifiers_comment_with_template(self):

        parser = KSSDocParser("""
            Style guide section title

            .emphasis - Adds brighter highlight.
            .subtle - Use for secondary actions.

                <p class="{{ modifier }}">The quick brown fox...</p>

            Styleguide 1.1
        """)
        self.assertTrue(parser.is_valid_section())

        section = parser.parse_section()
        self.assertEquals(section.title, 'Style guide section title')
        self.assertEquals(section.modifiers,
                          [{'description': 'Adds brighter highlight.',
                            'modifier': '.emphasis',
                            'template': '<p class="emphasis">The quick brown fox...</p>\n'},
                           {'description': 'Use for secondary actions.',
                            'modifier': '.subtle',
                            'template': '<p class="subtle">The quick brown fox...</p>\n'}])
        self.assertEquals(section.position, '1.1')
        self.assertEquals(section.template, '<p class="">The quick brown fox...</p>\n')



class StyleGuideSectionTest(TestCase):

    def test_order(self):

        s1_1 = StyleGuideSection('1.1','','',None,None)
        s1_1_1 = StyleGuideSection('1.1.1','','',None,None)
        s1_1_2 = StyleGuideSection('1.1.2','','',None,None)
        s1_2 = StyleGuideSection('1.2','','',None,None)
        s1_11 = StyleGuideSection('1.11','','',None,None)
        s1_21 = StyleGuideSection('1.21','','',None,None)

        expected_order = [s1_1, s1_1_1, s1_1_2, s1_2, s1_11, s1_21]
        sort_order = sorted(expected_order, key=lambda section: section.comparable_position())
        self.assertListEqual(sort_order, expected_order)



class SCSSCommentParserTest(TestCase):

    def setUp(self):
        self.source = """
This file is used for generic comment parsing across CSS, SCSS, SASS & LESS.

There's single-line comment styles:

// This comment block has comment identifiers on every line.
//
// Fun fact: this is Kyle's favorite comment syntax!


There's block comment styles:

/* This comment block is a block-style comment syntax.

There's only two identifier across multiple lines. */

/*
 * This is another common multi-line comment style.
 *
 * It has stars at the begining of every line.
 */


Some people do crazy things like mix comment styles:

// This comment has a /* comment */ identifier inside of it!

/* Look at my //cool// comment art! */


Indented comments:

    // Indented single-line comment.

    /* Indented block comment. */"""

        self.parser = SCSSCommentParser(self.source)

    def test_single_line_comment(self):
        self.assertTrue(self.parser.is_single_line_comment("// yuuuuup"))
        self.assertFalse(self.parser.is_single_line_comment("nooooope"))

    def test_start_multi_line_comment(self):
        self.assertTrue(self.parser.is_start_multi_line_comment("/* yuuuuup"))
        self.assertFalse(self.parser.is_start_multi_line_comment("nooooope"))

    def test_end_multi_line_comment(self):
        self.assertTrue(self.parser.is_end_multi_line_comment("yuuuuup */"))
        self.assertFalse(self.parser.is_end_multi_line_comment("nooooope"))

    def test_parse_single_line(self):
        self.assertEquals(self.parser.parse_single_line("// yuuuuup"), " yuuuuup")

    def test_parse_multi_line(self):
        self.assertEquals(self.parser.parse_multi_line("/* yuuuup */"), " yuuuup")

    def test_finds_single_line_comments(self):

        blocks = self.parser.blocks()
        self.assertIn(("This comment block has comment identifiers on every line.\n"
                       "\n"
                       "Fun fact: this is Kyle's favorite comment syntax!"), blocks)

    def test_finds_block_style_comments(self):

        blocks = self.parser.blocks()
        self.assertIn(("This comment block is a block-style comment syntax.\n"
                       "\n"
                       "There's only two identifier across multiple lines."), blocks)

    def test_finds_block_style_comments(self):

        blocks = self.parser.blocks()
        self.assertIn(("This comment block is a block-style comment syntax.\n"
                       "\n"
                       "There's only two identifier across multiple lines."), blocks)

        self.assertIn(("This is another common multi-line comment style.\n"
                       "\n"
                       "It has stars at the begining of every line."), blocks)

    def test_handles_mixed_styles(self):

        blocks = self.parser.blocks()
        self.assertIn("This comment has a /* comment */ identifier inside of it!", blocks)
        self.assertIn("Look at my //cool// comment art!", blocks)

    def test_handles_indented_comments(self):

        blocks = self.parser.blocks()
        self.assertIn("Indented single-line comment.", blocks)
        self.assertIn("Indented block comment.", blocks)
