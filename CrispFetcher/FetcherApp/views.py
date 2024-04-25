import datetime
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
		user.is_active,
	]
	return not False in user_validation_properties


def base_context(request, **args):
	context = {}
	user = request.user

	context["title"] = "none"
	context["user"] = "none"
	context["header"] = "none"
	context["error"] = 0
	context["message"] = ""
	context["is_superuser"] = False
	context["page_name"] = "default"

	if is_user_authenticated(request):

		context["username"] = user.username
		context["user"] = user

		if request.user.is_superuser:
			context["is_superuser"] = True

	if args != None:
		for arg in args:
			context[arg] = args[arg]

	return context


class CrispFetcher(View):
	def get(self, request):

		context = base_context(request)
		context["restore_editor"] = False
		context["page_name"] = "fetcher"
		return render(request, "fetcher.html", context)


class XMLsEditor(View, LoginRequiredMixin):
	def get(self, request, editor_id):

		if OpenedEditor.objects.filter(id=editor_id).exists():
			editor = OpenedEditor.objects.get(id=editor_id)
			if editor.user != request.user:
				return HttpResponseRedirect("/")
			context = base_context(request, title="Merger", header="Merger")

			context["restore_editor"] = True
			context["userOpenedEditorID"] = editor_id
			context["userOpenedEditor"] = editor.XMLs_editor_data
			context["oldXMLFilename"] = editor.old_XML_path.replace("\\", "/")
			context["newXMLFilename"] = editor.new_XML_path.replace("\\", "/")

			context["page_name"] = "editor"
			return render(request, "fetcher.html", context)

		context = base_context(request)
		context["page_name"] = "editor"
		return render(request, "fetcher.html", context)


class AjaxGetXMLs(View):
	def post(self, request):

		form = request.POST

		files = request.FILES

		oldXML = ""
		if "oldXML" in files:
			oldXML = files["oldXML"].read().decode("utf-8")

		newXML = ""
		if "newXML" in files:
			newXML = files["newXML"].read().decode("utf-8")

		xml_composer = XMLToStructureComposer("", "")

		xml_composer.old_XML = oldXML
		xml_composer.new_XML = newXML
		xml_composer.generate()

		response = {
			"result": "success",
			"oldXML": [obj.__dict__ for obj in xml_composer.new_old_XML_groups],
			"newXML": [obj.__dict__ for obj in xml_composer.new_new_XML_groups],
			"resXML": [obj.__dict__ for obj in xml_composer.res_XML_groups],
		}
		return JsonResponse(response, safe=False)


class AjaxSaveXMLs(View, LoginRequiredMixin):
	def post(self, request):
		form = request.POST

		editor_content = form["mainEditorState"]
		editor_id = int(form["userOpenedEditorID"])

		user = request.user

		if editor_id == -1:
			opened_editor = OpenedEditor(
				user=user,
				XMLs_editor_data=editor_content,
				datetime_created=datetime.datetime.now(),
				datetime_modified=datetime.datetime.now(),
				old_XML_path=form["oldXMLFilename"],
				new_XML_path=form["newXMLFilename"],
			)

			opened_editor.save()
		else:
			opened_editor = OpenedEditor.objects.get(id=editor_id)
			opened_editor.XMLs_editor_data = editor_content
			opened_editor.save()

		response = {"result": "success", "userOpenedEditorID": opened_editor.id}
		return JsonResponse(response, safe=False)


class RecentMerges(View):

	def get(self, request):
		context = base_context(request)
		context["page_name"] = "recent"

		context["openedEditors"] = list(OpenedEditor.objects.all())

		context["openedEditors"].reverse()

		return render(request, "recent.html", context)


class Login(View):

	def __init__(self):
		self.error = 0

	def get(self, request):
		context = base_context(request, title="Sing in", header="Sing in", error=0)
		context["error"] = 0
		return render(request, "signin.html", context)

	def post(self, request):
		context = {}
		form = request.POST

		username = form["username"]
		password = form["password"]

		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				context["name"] = username
				return HttpResponseRedirect("/")

		else:
			context = base_context(request, title="Вхід", header="Вхід")
			logout(request)
			context["error"] = 1
			# return Posts.get(self,request)
			return render(request, "signin.html", context)


class Logout(View):
	def get(self, request):
		logout(request)
		return HttpResponseRedirect("/")


class SignUp(View):
	def get(self, request):

		context = base_context(request, title="Sing up", header="Sing up", error=0)

		return render(request, "signup.html", context)

	def post(self, request):
		context = {}
		form = request.POST
		user_props = {}
		username = form["username"]
		password = form["password"]

		user_with_this_username_already_exists = bool(
			User.objects.filter(username=username)
		)
		if not user_with_this_username_already_exists:

			user = User.objects.create_user(
				username=form["username"],
				first_name=form["first_name"],
				password=form["password"],
			)

			user = authenticate(username=username, password=password)
			login(request, user)
			return HttpResponseRedirect("/")

		else:
			context = base_context(request, title="Sing up", header="Sing up")

			for field_name in form.keys():
				context[field_name] = form[field_name]

			context["error"] = 1
			return render(request, "signup.html", context)
