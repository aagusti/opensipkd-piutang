from ...views.base_views import BaseView
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
import colander

class PbbToolsView(BaseView):
    @view_config(route_name='pbb-tools', renderer='templates/home.pt',
                 permission='pbb-tools')
    def view_list(self):
        #rows = DBSession.query(Group).order_by('group_name')
        return dict(project = 'PBB Tools')
