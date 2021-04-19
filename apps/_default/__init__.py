from py4web import action, __version__
from .models import db


@action("index")
@action.uses("index.html")
def index():
    return dict(version=__version__)
