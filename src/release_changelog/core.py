from typing import Any, List

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
import pkg_resources
from sphinx.errors import SphinxError
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import nested_parse_with_titles

PROVIDER_ENTRYPOINT = 'release_changelog.providers'


logger = logging.getLogger(__name__)


class ReleasesError(SphinxError):
    category = 'Releases error'


def align_spec(argument):
    # type: (Any) -> str
    return directives.choice(argument, ('left', 'center', 'right'))


class Changelog(SphinxDirective):
    """
    Directive to insert changelog from release information
    """
    has_content = False
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        # type: () -> List[nodes.Node]
        if self.arguments:
            document = self.state.document
            repository_url = self.arguments[0]
        else:
            document = self.state.document
            return [document.reporter.warning(
                __('Changelog directive requires an argument corresponding to the repository url path'), line=self.lineno)]
        raw_rst = self.get_changelog_as_rst(repository_url)
        rst = ViewList()
        for i, line in enumerate(raw_rst.splitlines()):
            rst.append(line, "parsed-changelog", i+1)
        node = nodes.section()
        node.document = self.state.document

        # Parse the rst.
        nested_parse_with_titles(self.state, rst, node)

        # And return the result.
        return node.children

    @staticmethod
    def get_changelog_as_rst(repository_url):
        providers = [ep.load() for ep in pkg_resources.iter_entry_points(PROVIDER_ENTRYPOINT) if ep.name is not None]
        for provider in providers:
            if provider.check_url(repository_url):
                return provider.convert(repository_url)
        raise ReleasesError(f'No Provider found for {repository_url}')
