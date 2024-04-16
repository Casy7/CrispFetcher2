import json
from django.shortcuts import render


from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import View

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.contrib.auth.models import AnonymousUser

from CrispFetcher.settings import MEDIA_ROOT
from .models import *
from .code.fetcher import *

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

		files = request.FILES

		oldXML = ""
		if 'oldXML' in files:
			oldXML = files['oldXML'].read().decode("utf-8")
		
		newXML = ""
		if 'newXML' in files:
			newXML = files['newXML'].read().decode("utf-8")

		xml_composer = XMLToStructureComposer("", "")

		xml_composer.old_XML = oldXML
		xml_composer.new_XML = newXML
		xml_composer.generate()

		response = {
			"result" : "success",
			"oldXML" : [obj.__dict__ for obj in xml_composer.new_old_XML_groups],
			"newXML" : [obj.__dict__ for obj in xml_composer.new_new_XML_groups],
			"resXML" : [obj.__dict__ for obj in xml_composer.res_XML_groups]
		}
		return JsonResponse(response, safe=False)