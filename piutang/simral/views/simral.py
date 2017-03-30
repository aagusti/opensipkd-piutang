from pyramid.view import (view_config,)
from pyramid.httpexceptions import ( HTTPFound, )
from ..views import SimralView
class HomeView(SimralView):
    @view_config(route_name="simral", renderer="templates/home.pt",
                 permission="simral")
    def view(self):
        return dict(project=self.project)
        
    @view_config(route_name="simral-ws", renderer="templates/ws.pt")
    def ws(self):
        return dict(project=self.project)        