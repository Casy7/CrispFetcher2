"use strict"
;(function (document, window, index) {
	// feature detection for drag&drop upload
	var isAdvancedUpload = (function () {
		var div = document.createElement("div")
		return ("draggable" in div || ("ondragstart" in div && "ondrop" in div)) && "FormData" in window && "FileReader" in window
	})()

	let oldXML = NaN
	let newXML = NaN

	// applying the effect for every form
	var forms = document.querySelectorAll(".box")
	Array.prototype.forEach.call(forms, function (form) {
		var input = form.querySelector('input[type="file"]'),
			label = form.querySelector("label"),
			errorMsg = form.querySelector(".box__error span"),
			restart = form.querySelectorAll(".box__restart"),
			droppedFiles = false,
			showFiles = function (files) {
				label.textContent = files.length > 1 ? (input.getAttribute("data-multiple-caption") || "").replace("{count}", files.length) : files[0].name
			}

		// letting the server side to know we are going to make an Ajax request
		var ajaxFlag = document.createElement("input")
		ajaxFlag.setAttribute("type", "hidden")
		ajaxFlag.setAttribute("name", "ajax")
		ajaxFlag.setAttribute("value", 1)
		form.appendChild(ajaxFlag)

		// automatically submit the form on file select
		input.addEventListener("change", function (e) {
			showFiles(e.target.files)

			// triggerFormSubmit()
		})

		// drag&drop files if the feature is available
		if (isAdvancedUpload) {
			form.classList.add("has-advanced-upload") // letting the CSS part to know drag&drop is supported by the browser
			;["drag", "dragstart", "dragend", "dragover", "dragenter", "dragleave", "drop"].forEach(function (event) {
				form.addEventListener(event, function (e) {
					// preventing the unwanted behaviours
					e.preventDefault()
					e.stopPropagation()
				})
			})
			;["dragover", "dragenter"].forEach(function (event) {
				form.addEventListener(event, function () {
					form.classList.add("is-dragover")
				})
			})
			;["dragleave", "dragend", "drop"].forEach(function (event) {
				form.addEventListener(event, function () {
					form.classList.remove("is-dragover")
				})
			})
			form.addEventListener("drop", function (e) {
				droppedFiles = e.dataTransfer.files // the files that were dropped
				showFiles(droppedFiles)

				triggerFormSubmit()
			})
		}

		// if the form was submitted
		form.addEventListener("submit", function (e) {
			// preventing the duplicate submissions if the current one is in progress
			if (form.classList.contains("is-uploading")) return false

			form.classList.add("is-uploading")
			form.classList.remove("is-error")

			if (isAdvancedUpload) {
				// ajax file upload for modern browsers
				e.preventDefault()

				// gathering the form data
				var ajaxData = new FormData(form)
				if (droppedFiles) {
					Array.prototype.forEach.call(droppedFiles, function (file) {
						ajaxData.append(input.getAttribute("name"), file)
					})
				}
			} // fallback Ajax solution upload for older browsers
			else {
				var iframeName = "uploadiframe" + new Date().getTime(),
					iframe = document.createElement("iframe")

				$iframe = $('<iframe name="' + iframeName + '" style="display: none;"></iframe>')

				iframe.setAttribute("name", iframeName)
				iframe.style.display = "none"

				document.body.appendChild(iframe)
				form.setAttribute("target", iframeName)

				iframe.addEventListener("load", function () {
					var data = JSON.parse(iframe.contentDocument.body.innerHTML)
					form.classList.remove("is-uploading")
					form.classList.add(data.success == true ? "is-success" : "is-error")
					form.removeAttribute("target")
					if (!data.success) errorMsg.textContent = data.error
					iframe.parentNode.removeChild(iframe)
				})
			}
		})

		// restart the form if has a state of error/success
		Array.prototype.forEach.call(restart, function (entry) {
			entry.addEventListener("click", function (e) {
				e.preventDefault()
				form.classList.remove("is-error", "is-success")
				input.click()
			})
		})

		// Firefox focus bug fix for file input
		input.addEventListener("focus", function () {
			input.classList.add("has-focus")
		})
		input.addEventListener("blur", function () {
			input.classList.remove("has-focus")
		})
	})
})(document, window, 0)

function getCookie(name) {
	var cookieValue = null
	if (document.cookie && document.cookie !== "") {
		var cookies = document.cookie.split(";")
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i])
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === name + "=") {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
				break
			}
		}
	}
	return cookieValue
}

const send = document.querySelector("#sendXMLsButton")

send.addEventListener("click", async () => {
	// A <form> element
	const userInfo = document.querySelector("#XMLs")
	const formData = new FormData(userInfo)

	const oldXMLFilename = document.querySelector("#old_XML").value.split(/(\\|\/)/g).pop()
	const newXMLFilename = document.querySelector("#new_XML").value.split(/(\\|\/)/g).pop()

	const response = await fetch("/upload_xmls/", {
		method: "POST",
		body: formData,
		credentials: "same-origin",
		headers: {
			"X-CSRFToken": getCookie("csrftoken"),
		},
	})
		.then((response) => response.json())
		.then((data) => {
			// console.log(data)
			update_xmls(data.oldXML, data.newXML, data.resXML);
			$("#XMLSelectorModal").hide();

			$(".oldXMLFileName").text("Old - " + oldXMLFilename);
			$(".newXMLFileName").text("New - " + newXMLFilename);
			
		})
})
