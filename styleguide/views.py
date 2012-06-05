from django.core.urlresolvers import reverse
from django.views.generic import RedirectView
from django.views.generic.base import TemplateView
from styleguide.builder import StyleGuideBuilder
from styleguide.collector import FileCollector



class IndexView(RedirectView):

    def get_redirect_url(self, **kwargs):
        default_position = "1"
        url = reverse("styleguide_section",
                      kwargs={"position": default_position})
        return url


class SectionView(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        request.position = kwargs.get("position", "1")
        return super(SectionView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        builder = StyleGuideBuilder(FileCollector())
        guide = builder.get_style_guide()

        sections = guide.get_sections(position=self.request.position)
        top_links = self.get_top_links(guide)

        return {
            "guide": guide,
            "sections": sections,
            "top_links": top_links,
        }

    def get_template_names(self):

        override_template_name = "styleguide/styleguide_%s.html" \
                                 % self.request.position
        base_template_name = "styleguide/styleguide.html"
        return [override_template_name, base_template_name]

    def get_top_links(self, guide):

        root_sections = guide.get_root_sections()
        top_links = []
        for section in root_sections:
            name = "%s. %s" % (section.position, section.title)
            url = reverse("styleguide_section",
                          kwargs={"position": section.position})
            top_links.append((name, url))
        return top_links
