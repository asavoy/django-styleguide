import re
from pkg_resources import parse_version



class StyleGuide(object):
    """
    A StyleGuide has many sections of stylesheet documentation.
    """

    def __init__(self, title, sections):
        self.title = title
        self.sections = sections

    def get_sections(self, position=""):
        if position != "":
            position = position.rstrip(".")
            prefix_position_re = re.compile("^" + re.escape(position) + r"($|\.)")
            return [s for s in self.sections if prefix_position_re.search(s.position)]
        else:
            return self.sections

    def get_root_sections(self):
        return filter(lambda s: s.depth() == 0, self.sections)

    def __unicode__(self):
        return u"%s" % self.title

    def __repr__(self):
        return u"<StyleGuide %s>" % unicode(self)



class StyleGuideSection(object):
    """
    A section of stylesheet documentation.
    """

    def __init__(self, position, title, desc, modifiers, template):
        self.position = position.rstrip(".")
        self.title = title
        self.desc = desc
        self.modifiers = modifiers
        self.template = template

    def comparable_position(self):
        return parse_version(self.position)

    def depth(self):
        return len(filter(lambda c: c==".", self.position))

    def __unicode__(self):
        return u"%s %s" % (self.position, self.title)

    def __repr__(self):
        return u"<StyleGuideSection %s>" % unicode(self)
