var totalLinesAmount = 0;
var totalSpacesBeforeItem = 0;

let userOpenedEditorID = -1;

function update_xmls(oldXMLStructure, newXMLStructure, resXMLStructure) {


    add_lines_to(oldXMLStructure, document.getElementById('oldXML'));
    add_group_move_btns_from_old(oldXMLStructure);

    add_line_numbers('oldXMLLineNumberCol', oldXMLStructure)



    add_lines_to(newXMLStructure, document.getElementById('newXML'));

    add_move_btns_to_old_xml_col();
    add_move_btns_to_new_xml_col();

    add_group_move_btns_from_new(newXMLStructure);

    add_line_numbers('newXMLLineNumberCol', newXMLStructure);

    add_lines_to(resXMLStructure, document.getElementById('resXML'));

}

function add_lines_to(lines, el) {

  curr_line = 0;

  for (i = 0; i < lines.length; i++) {
    if (Object.keys(lines[i]).find(el => el == 'raw_lines')) {
      for (curr_group_line = 0; curr_group_line < lines[i]['raw_lines'].length; curr_group_line++) {
        compile_template(el.id + "_" + curr_line, lines[i]['raw_lines'][curr_group_line], el);
        curr_line++;
      }
      if (totalSpacesBeforeItem == 0) {
        if (lines[i]['raw_lines'][0].search("<item ") > -1) {
          totalSpacesBeforeItem = lines[i]['raw_lines'][0].length - lines[i]['raw_lines'][0].trimLeft().length;
        }
      }
    }
    else if (Object.keys(lines[i]).find(el => el == 'raw_line')) {
      compile_template(el.id + "_" + curr_line, lines[i]['raw_line'], el);
      curr_line++;
    }
  }
  totalLinesAmount = curr_line;
}


function add_move_btns_to_old_xml_col() {
  for (i = 0; i < totalLinesAmount; i++) {
    $('#move_from_old').append($(`
        <div>
          <pre class="center moveLineFromOldBtn" onclick='move_line_from_old(`+i+`)'>❭</pre>
        </div>
        `));
  }
}

function add_move_btns_to_new_xml_col() {
  for (i = 0; i < totalLinesAmount; i++) {
    $('#move_from_new').append($(`
        <div>
          <pre class="center moveLineFromOldBtn" onclick='move_line_from_new(`+i+`)'>❭</pre>
        </div>
        `));
  }
}

function add_group_move_btns_to(lines, el) {

  curr_group_index = 0;

  for (i = 0; i < lines.length; i++) {
    if (Object.keys(lines[i]).find(el => el == 'raw_line')) {
      $(el).append($(`
      <div>
        <pre class="" style="height: 15px"></pre>
      </div>
      `));
    }
    else if (Object.keys(lines[i]).find(el => el == 'raw_lines')) {
      additionalClass = "";
      if (lines[i]['raw_lines'].length == 1) {
        additionalClass = "smallText";
      }
      $(el).append($(`
        <div>
          <p class="groupMoveBtn `+ additionalClass + `" id="moveLineGroupFromOld_` + curr_group_index + `" style="height: ` + 15 * (lines[i]['raw_lines'].length) + `px">❭❭</p>
        </div>
        `));
      curr_group_index++;
    }
  }
}

function compile_template(line_id, line_content, append_to) {

  let line_parts = [["", line_content]];
  let raw_line = line_content;
  let i = 0;
  while (i < line_parts.length) {
    let curr_classes = line_parts[i][0];
    let curr_part = line_parts[i][1];
    if (curr_part.search('%FROM_NEW_XML_START%') > -1 && curr_part.search('%FROM_NEW_XML_END%') > -1) {
      tm_start = curr_part.search('%FROM_NEW_XML_START%');
      tm_end = curr_part.search('%FROM_NEW_XML_END%');
      line_parts[i] = [curr_classes, curr_part.substr(0, tm_start)];
      line_parts.splice(i + 1, 0, [curr_classes + " fromNewXMLLine", curr_part.substr(tm_start, tm_end+"%FROM_NEW_XML_END%".length-tm_start).replace('%FROM_NEW_XML_START%', '').replace('%FROM_NEW_XML_END%', '')]);
      line_parts.splice(i + 2, 0, [curr_classes, curr_part.substr(tm_end+'%FROM_NEW_XML_END%'.length, curr_part.length)]);
      // console.log(2);
    }
    if (curr_part.search('%EQUAL_IN_BOTH_XMLS_START%') > -1 && curr_part.search('%EQUAL_IN_BOTH_XMLS_END%') > -1) {
      tm_start = curr_part.search('%EQUAL_IN_BOTH_XMLS_START%');
      tm_end = curr_part.search('%EQUAL_IN_BOTH_XMLS_END%');
      line_parts[i] = [curr_classes, curr_part.substr(0, tm_start)];
      line_parts.splice(i + 1, 0, [curr_classes + " equalInBothXMLsLine", curr_part.substr(tm_start, tm_end+"%EQUAL_IN_BOTH_XMLS_END%".length-tm_start).replace('%EQUAL_IN_BOTH_XMLS_START%', '').replace('%EQUAL_IN_BOTH_XMLS_END%', '')]);
      line_parts.splice(i + 2, 0, [curr_classes, curr_part.substr(tm_end+'%EQUAL_IN_BOTH_XMLS_END%'.length, curr_part.length)]);
      // console.log(2);
    }    
    /*   +
    
    else if (template_1 condition) { 
      template_1 action
    }
    else if (template_2 condition) { 
      template_2 action
    }
    ...

    */
    else {
      i++;
    }
  }


  $(append_to).append($("<div class='lineBox' id=\""+line_id+"\"></div>"));

  for (i = 0; i < line_parts.length; i++) {
    let curr_line_content = line_parts[i][1];
    let curr_line_classes = line_parts[i][0];
    let additionalClasses = "";
    if (curr_line_content == "%GRAYLINE%") {
      additionalClasses += " grayLine";
      curr_line_content = ""
    }

    if (curr_line_content == "%REDLINE%") {
      additionalClasses += " redLine";
      curr_line_content = ""
    }

    if (curr_line_content.search('%REDLINE%') > -1) {
      additionalClasses += " redLine";
      curr_line_content = curr_line_content.replace('%REDLINE%', "");
    }

    if (curr_line_content.search('%LINE_FROM_OLD_XML%') > -1) {
      curr_line_content = curr_line_content.replace('%LINE_FROM_OLD_XML%', "");
      additionalClasses += " fromOldXMLLine";
    }
    if (curr_line_content.search('%LINE_FROM_NEW_XML%') > -1) {
      curr_line_content = curr_line_content.replace('%LINE_FROM_NEW_XML%', "");
      additionalClasses += " fromNewXMLLine";
    }

    if (curr_line_content.search('%EQUAL_IN_BOTH_XMLS_LINE%') > -1) {
      curr_line_content = curr_line_content.replace('%EQUAL_IN_BOTH_XMLS_LINE%', "");
      additionalClasses += " equalInBothXMLsLine";
    }    


    if (additionalClasses.length) {
      $("#"+line_id).addClass(additionalClasses);
      document.getElementById(line_id).className = document.getElementById(line_id).className + " " + additionalClasses;
    }

    $("#"+line_id).append($(`<pre class="line `+ additionalClasses + curr_line_classes+`" id="` + line_id + `_`+i+`"></pre>`));
    
    $("#" + line_id + "_"+i).text(curr_line_content);
  }
}

function auto_grow(element) {
  element.style.height = "5px";
  element.style.height = (element.scrollHeight) + "px";
}

function add_line_numbers(numbers_container, xml_structure) {
  let line_index = 0;
  for (i = 0; i < xml_structure.length; i++) {
    // console.log(xml_structure[i]);
    if (Object.keys(xml_structure[i]).find(el => el == 'raw_line')) {
      if (xml_structure[i]['raw_line'] != "%GRAYLINE%" && xml_structure[i]['raw_line'] != "%REDLINE%") {
      $('#'+numbers_container).append($(`
      <div>
        <pre class="lineNumber">`+ (line_index + 1) + `</pre>
      </div>
      `));
      line_index++;
    }
      else {
        $('#'+numbers_container).append($(`
        <div>
          <pre class="lineNumber"> </pre>
        </div>
        `));
      }
    }
    else if (Object.keys(xml_structure[i]).find(el => el == 'raw_lines')) {
      additionalClass = "";
      for (j=0; j<xml_structure[i]['raw_lines'].length; j++) {
        $('#'+numbers_container).append($(`
        <div>
          <pre class="lineNumber">`+ (line_index + 1) + `</pre>
        </div>
        `));
        line_index++;
      }
    }
  }
}

async function show_copied_popover(ms) {
  $("#popoverCopied").removeClass("hidden");
  $("#popoverCopied").removeClass("hide");
  $("#popoverCopied").addClass("show");
	await new Promise(resolve => setTimeout(resolve, ms));
  $("#popoverCopied").removeClass("show");
  $("#popoverCopied").addClass("hide");
  }

  async function show_saved_popover(ms) {
    $("#popoverSaved").removeClass("hidden");
    $("#popoverSaved").removeClass("hide");
    $("#popoverSaved").addClass("show");
    await new Promise(resolve => setTimeout(resolve, ms));
    $("#popoverSaved").removeClass("show");
    $("#popoverSaved").addClass("hide");
    }


function copy_result() {
  let res = document.getElementById("resXML");
  // console.log(res.childNodes);
  let res_str = "";
  res.childNodes.forEach((element) => {
    if (element.innerText != undefined && element.className.search("redLine") == -1 && element.className.search("grayLine") == -1){
      res_str +=getInnerText(element)+"\n";
    }

  });
  res_str = res_str.replace(/\r\n/g, '\n').replace(/\n\n\n\n+/g, '\n\n').replace(/(<\/item>\n\n<)/g, '</item>\n\n\n<');
  fallbackCopyTextToClipboard(res_str);
  i = 0;
  show_copied_popover(1000);
  
}

function getInnerText(el) {
  el_text = "";
  if (el.childNodes.length) {
    el.childNodes.forEach((element) => {
      if (element.innerText != undefined){
        el_text += element.innerText;  
      }
  
    });
  }
  else {
    el_text = element.innerText;
  }
  return el_text;
}

function fallbackCopyTextToClipboard(text) {
  var textArea = document.createElement("textarea");
  textArea.value = text;
  
  // Avoid scrolling to bottom
  textArea.style.top = "0";
  textArea.style.left = "0";
  textArea.style.position = "fixed";

  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  try {
    var successful = document.execCommand('copy');
    var msg = successful ? 'successful' : 'unsuccessful';
    console.log('Fallback: Copying text command was ' + msg);
  } catch (err) {
    console.error('Fallback: Oops, unable to copy', err);
  }

  document.body.removeChild(textArea);
}
function copyTextToClipboard(text) {
  if (!navigator.clipboard) {
    fallbackCopyTextToClipboard(text);
    return;
  }
  navigator.clipboard.writeText(text).then(function() {
    console.log('Async: Copying to clipboard was successful!');
  }, function(err) {
    console.error('Async: Could not copy text: ', err);
  });
}

function move_line_from_old(line_index) {
  let old_line = document.getElementById('oldXML_'+line_index);
  let res_line = document.getElementById('resXML_'+line_index);
  res_line.innerHTML = `<pre class="line " id="resXML_`+line_index+`_0"></pre>` ;
  $("#resXML_"+line_index+"_0").text(old_line.innerText);
  res_line.className = "lineBox fromOldXMLLine";
}

function move_line_from_new(line_index) {
  let new_line = document.getElementById('newXML_'+line_index);
  let res_line = document.getElementById('resXML_'+line_index);
  res_line.innerHTML = `<pre class="line " id="resXML_`+line_index+`_0"></pre>` ;
  $("#resXML_"+line_index+"_0").text(' '.repeat(totalSpacesBeforeItem) + new_line.innerText);
  res_line.className = "lineBox fromNewXMLLine";
}

function add_group_move_btns_from_old(lines) {

  el = document.getElementById('move_group_from_old');
  curr_group_index = 0;
  curr_line_index = 0;

  for (i = 0; i < lines.length; i++) {
    if (Object.keys(lines[i]).find(el => el == 'raw_line')) {
      $(el).append($(`
      <div>
        <pre class="" style="height: 15px"></pre>
      </div>
      `));
      curr_line_index++;
    }
    else if (Object.keys(lines[i]).find(el => el == 'raw_lines')) {
      additionalClass = "";
      if (lines[i]['raw_lines'].length == 1) {
        additionalClass = "smallText";
      }
      $(el).append($(`
        <div>
          <p class="groupMoveBtn `+ additionalClass + `" id="moveLineGroupFromOld_` + curr_group_index + `" style="height: ` + 15 * (lines[i]['raw_lines'].length) + `px" onclick='move_group_lines_from_old(`+curr_line_index+`, `+(curr_line_index+(lines[i]['raw_lines'].length))+`)'>❭❭</p>
        </div>
        `));
      curr_line_index+=(lines[i]['raw_lines'].length);
      curr_group_index++;
    }
  }
}

function move_group_lines_from_old(start_line, end_line) {
  for (i=start_line; i<end_line; i++) {
    move_line_from_old(i);
  }
}



function add_group_move_btns_from_new(lines) {

  el = document.getElementById('move_group_from_new');
  curr_group_index = 0;
  curr_line_index = 0;

  for (i = 0; i < lines.length; i++) {
    if (Object.keys(lines[i]).find(el => el == 'raw_line')) {
      $(el).append($(`
      <div>
        <pre class="" style="height: 15px"></pre>
      </div>
      `));
      curr_line_index++;
    }
    else if (Object.keys(lines[i]).find(el => el == 'raw_lines')) {
      additionalClass = "";
      if (lines[i]['raw_lines'].length == 1) {
        additionalClass = "smallText";
      }
      $(el).append($(`
        <div>
          <p class="groupMoveBtn `+ additionalClass + `" id="moveLineGroupFromNew_` + curr_group_index + `" style="height: ` + 15 * (lines[i]['raw_lines'].length) + `px" onclick='move_group_lines_from_new(`+curr_line_index+`, `+(curr_line_index+(lines[i]['raw_lines'].length))+`)'>❭❭</p>
        </div>
        `));
      curr_line_index+=(lines[i]['raw_lines'].length);
      curr_group_index++;
    }
  }
}

function move_group_lines_from_new(start_line, end_line) {
  for (i=start_line; i<end_line; i++) {
    move_line_from_new(i);
  }
}

function move_to_top(){
  $("html, body").animate({ scrollTop: 0 }, "slow");
}



$(document).ready(function () {
  $("#XMLFileNames").fadeTo(1, 0.1);
	function isScrolledFromTop() {
		return $(window).scrollTop() > 200;
	}

	// Функция для выполнения AJAX запроса при достижении конца страницы
	function showFileNames() {
		// Проверяем, долистал ли пользователь страницу до конца
		if (isScrolledFromTop()) {
      $("#XMLFileNames").fadeTo(1, 1);
		}
    else {
      $("#XMLFileNames").fadeTo(1, 0.01);
    }
	}

	// Обработчик события прокрутки страницы
	$(window).scroll(function () {
		// Выполняем AJAX запрос при достижении конца страницы
		showFileNames();
	});
});

function myFunction() {
  var popup = document.getElementById("myPopup");
  popup.classList.toggle("show");
}

async function saveXMLs() {
  show_saved_popover(1000);
  

  let mainEditor = document.getElementById('mainEditor');

  // const formData = new FormData();

  // formData.append("userOpenedEditorID", userOpenedEditorID);
  // formData.append("mainEditorState", mainEditor.innerHTML);

  const oldXMLFilename = document.querySelector("#old_XML").value;
	const newXMLFilename = document.querySelector("#new_XML").value;

  // formData.append("oldXMLFilename", oldXMLFilename);
  // formData.append("newXMLFilename", newXMLFilename);

  $.ajax({
    url: "/save_xmls/",
    type: 'POST',
    data: {
      'userOpenedEditorID': userOpenedEditorID,
      "mainEditorState": mainEditor.innerHTML,
      "oldXMLFilename": oldXMLFilename,
      "newXMLFilename": newXMLFilename
    },
    beforeSend: function (xhr) {
      function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      }
      csrftoken_val = collectCookies(xhr);
      csrftoken_val = getCookie('csrftoken');
      if (csrftoken_val == "") {
        csrftoken_val = document.getElementsByName('csrfmiddlewaretoken')[0].value;
      }
      xhr.setRequestHeader('X-CSRF-Token', csrftoken_val);
    },
    success: function a(json) {
      if (json.result === "success") {
        userOpenedEditorID = json.userOpenedEditorID;
        $(".checked-icon").addClass("checked");
      } else {

      }
    }
  });

}