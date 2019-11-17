from typing import Any, Dict

import sphinx
from sphinx.application import Sphinx

from release_changelog.core import Changelog
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_directive('changelog', Changelog)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
