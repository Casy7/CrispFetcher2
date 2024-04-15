import json
from django.shortcuts import render


from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.contrib.auth.models import AnonymousUser

from CrispFetcher.settings import MEDIA_ROOT
from .models import *

def is_user_authenticated(request):
	user = request.user
	user_validation_properties = [
		request.user != None,
		not request.user.is_anonymous,
		type(request.user) != AnonymousUser,
		len(User.objects.filter(username=user.username)) != 0,
		user.is_active
	]
	return not False in user_validation_properties

def base_context(request, **args):
	context = {}
	user = request.user

	context['title'] = 'none'
	context['user'] = 'none'
	context['header'] = 'none'
	context['error'] = 0
	context['message'] = ''
	context['is_superuser'] = False
	context['page_name'] = 'default'

	if is_user_authenticated(request):

		context['username'] = user.username
		context['user'] = user

		if request.user.is_superuser:
			context['is_superuser'] = True

	if args != None:
		for arg in args:
			context[arg] = args[arg]

	return context

class CrispFetcher(View):
	def get(self, request):
		
		context = base_context(request)
		context['page_name'] = 'fetcher'
		return render(request, "fetcher.html", context)
	

class AjaxGetXMLs(View):
	def post(self, request):

		form = request.POST

		result = {}
		return HttpResponse(json.dumps(result),
			content_type="application/json"
		)