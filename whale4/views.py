
from django.template import RequestContext
from django.shortcuts import render_to_response


def bad_request(request):
    response = render_to_response('whale4/400.html', {},context_instance=RequestContext(request))
    response.status_code = 400
    return response

def permission_denied(request):
    response = render_to_response('whale4/403.html', {},context_instance=RequestContext(request))
    response.status_code = 403
    return response

def page_not_found(request):
    response = render_to_response('whale4/404.html', {},context_instance=RequestContext(request))
    response.status_code = 404
    return response


def server_error(request):
    response = render_to_response('whale4/500.html', {},context_instance=RequestContext(request))
    response.status_code = 500
    return response