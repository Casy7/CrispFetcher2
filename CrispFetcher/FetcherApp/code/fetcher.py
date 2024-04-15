import xml.etree.ElementTree as ET
from .fetcher_funcs import *
import copy


class XMLObject:
	def __init__(self) -> None:
		pass

	def length(self) -> int:
		return 0

	def add_XML_class(self, className: str) -> None:
		pass

	def add_XML_prefix(self, prefix: str) -> None:
		pass

class XMLGroup(XMLObject):
	def __init__(self, start_line, raw_lines) -> None:
		self.raw_lines = raw_lines
		self.start_line = start_line
		self.end_line = start_line + len(raw_lines) - 1

	def length(self):
		return self.end_line - self.start_line + 1

	def add_XML_class(self, className):
		for line_index in range(len(self.raw_lines)):

			self.raw_lines[line_index] = f"%"+className+"%" + self.raw_lines[line_index]


	def add_XML_prefix(self, prefix: str) -> None:
		for line_index in range(len(self.raw_lines)):

			self.raw_lines[line_index] = prefix + self.raw_lines[line_index]


class XMLLine(XMLObject):
	def __init__(self, line_number, raw_line) -> None:
		self.raw_line = raw_line
		self.line_number = line_number

	def length(self):
		return 1

	def add_XML_class(self, className: str) -> None:
		self.raw_line = "%"+ className +"%" + self.raw_line

	def add_XML_prefix(self, prefix: str) -> None:
		self.raw_line = prefix + self.raw_line




class XMLGrayLine(XMLLine):
	def __init__(self) -> None:
		self.raw_line = f"%GRAYLINE%"
		self.line_number = -1


class XMLRedLine(XMLLine):
	def __init__(self) -> None:
		self.raw_line = f"%REDLINE%"
		self.line_number = -1


class Item(XMLGroup):
	def __init__(self, start_line:int, raw_lines:list) -> None:
		super().__init__(start_line, raw_lines)
		self.name = ""
		self.image_path = ""
		self.unique_name = ""
		self.translated_name = ""
		self.type = ""
		self.rect_attrs = dict({})
		self.item_decompose(self.raw_lines)

	def item_decompose(self, raw_lines):
		raw_text = rec_replace(" ".join(raw_lines), "  ", " ")
		self.name = get_text_between(raw_text, "<name>", "</name>")
		self.image_path = get_text_between(
			raw_text, "<image path=\"", "\"></image>")
		for raw_attr in re.findall(r"[A-Za-z]* ?=\"[^\"]{0,40}\"", raw_text):
			# raw_attr = str(raw_attr)
			arg_name = raw_attr[:raw_attr.find("=")]
			arg_val = get_text_between(raw_attr, "\"", "\"")
			self.rect_attrs[arg_name] = arg_val
		self.type = self.rect_attrs["type"]
		pass

	def set_name(self, new_name):

		for i in range(len(self.raw_lines)):
			line = self.raw_lines[i]
			if "<name>" in line and "</name>" in line:
				self.raw_lines[i] = line[:line.find("<name>")+len("<name>")] + new_name + line[line.find("</name>"):]
				self.name = new_name
				break

	def set_tag(self, tag_name, tag_value):

		for i in range(len(self.raw_lines)):
			line = self.raw_lines[i]

			tag_in_line = re.search(r"("+tag_name+r") ?=\"", line)
			self.rect_attrs[tag_name] = tag_value
			if tag_in_line:
				self.raw_lines[i] = line[:tag_in_line.span()[1]] + tag_value + line[tag_in_line.span()[1]:][line[tag_in_line.span()[1]+1:].find("\"")+1:]
				break


	def merge_with_new(self, new_item):

		res_item = Item(self.start_line, self.raw_lines.copy())

		if self.name == new_item.name:
			res_item.set_name(f"%EQUAL_IN_BOTH_XMLS_START%"+new_item.name+f"%EQUAL_IN_BOTH_XMLS_END%")
		else:
			res_item.set_name(f"%FROM_NEW_XML_START%"+new_item.name+f"%FROM_NEW_XML_END%")
		
		res_item.image_path = new_item.image_path

		for arg in ("x", "y", "width", "height", "path", "type"):

			if self.rect_attrs[arg] == new_item.rect_attrs[arg]:
				res_item.set_tag(arg, f"%EQUAL_IN_BOTH_XMLS_START%"+new_item.rect_attrs[arg]+f"%EQUAL_IN_BOTH_XMLS_END%")
			else:
				res_item.set_tag(arg, f"%FROM_NEW_XML_START%"+new_item.rect_attrs[arg]+f"%FROM_NEW_XML_END%")

		res_item.add_XML_class("LINE_FROM_OLD_XML")
		return res_item


class GrayLineList:
	def __init__(self) -> None:
		self.list = []
		self.curr_line = 0
		self.result_from = "old"

	def has_next(self):
		if self.this_line < len(self.list-1):
			return True
		return False

	def next(self):
		self.curr_line += 1
		return self.list[self.curr_line]


class XMLToStructureComposer():
	def __init__(self, oldXML, newXML) -> None:
		self.old_XML = self.normalize_xml(oldXML)
		self.new_XML = self.normalize_xml(newXML)

		self.old_XML_list = []
		self.new_XML_list = []

		self.old_XML_groups = []
		self.new_XML_groups = []

		self.new_old_XML_groups = []
		self.new_new_XML_groups = []
		self.res_XML_groups = []

	def generate(self):
		self.old_XML_list = self.get_XML_list(self.old_XML)
		self.new_XML_list = self.get_XML_list(self.new_XML)

		self.old_XML_groups = self.group_compose(self.old_XML_list)
		self.new_XML_groups = self.group_compose(self.new_XML_list)

		self.new_old_XML_groups = self.new_group_compose(self.old_XML_list)
		self.new_new_XML_groups = self.new_group_compose(self.new_XML_list)

		self.generate_struct()

	def normalize_xml(self, xml):
		return xml.replace("\u200b", "\t").replace("​", "\n").replace("< ", "<")

	def get_XML_list(self, xml_content):
		xml_list = xml_content.split('\n')
		return xml_list

	@property
	def old_struct(self):
		return self.generate_struct(self.old_xml)

	def group_compose(self, xml_list):
		groups = []
		groups_new = []

		curr_line_start_group_index = 0
		while curr_line_start_group_index < len(xml_list):
			start_group = curr_line_start_group_index
			end_group = curr_line_start_group_index
			if "<item " in xml_list[curr_line_start_group_index]:
				start_group = curr_line_start_group_index
				for curr_line_end_group_index in range(curr_line_start_group_index, len(xml_list)):
					if "</item>" in xml_list[curr_line_end_group_index]:
						end_group = curr_line_end_group_index
						groups.append((start_group, end_group))
						groups_new.append(
							Item(start_group, xml_list[start_group:end_group+1]))
						curr_line_start_group_index = curr_line_end_group_index+1
						break
				curr_line_start_group_index += 1
			elif "<scene" in xml_list[curr_line_start_group_index]:
				for curr_line_end_group_index in range(curr_line_start_group_index, len(xml_list)):
					if ">" in xml_list[curr_line_end_group_index]:
						end_group = curr_line_end_group_index
						groups.append((start_group, end_group))
						curr_line_start_group_index = curr_line_end_group_index+1
						break

			elif "<?xml" in xml_list[curr_line_start_group_index]:
				for curr_line_end_group_index in range(curr_line_start_group_index, len(xml_list)):
					if ">" in xml_list[curr_line_end_group_index]:
						end_group = curr_line_end_group_index
						groups.append((start_group, end_group))
						curr_line_start_group_index = curr_line_end_group_index+1
						break
			

			else:
				groups_new.append(
					XMLLine(curr_line_start_group_index, xml_list[curr_line_start_group_index]))
				curr_line_start_group_index += 1

		return groups

	def new_group_compose(self, xml_list):

		groups_new = []

		curr_line_start_group_index = 0
		while curr_line_start_group_index < len(xml_list):
			start_group = curr_line_start_group_index
			end_group = curr_line_start_group_index
			if "<item " in xml_list[curr_line_start_group_index]:
				start_group = curr_line_start_group_index
				for curr_line_end_group_index in range(curr_line_start_group_index, len(xml_list)):
					if "</item>" in xml_list[curr_line_end_group_index]:
						end_group = curr_line_end_group_index
						groups_new.append(
							Item(start_group, xml_list[start_group:end_group+1]))
						curr_line_start_group_index = curr_line_end_group_index+1
						break
				# curr_line_start_group_index += 1
			elif "<scene" in xml_list[curr_line_start_group_index]:
				for curr_line_end_group_index in range(curr_line_start_group_index, len(xml_list)):
					if ">" in xml_list[curr_line_end_group_index]:
						end_group = curr_line_end_group_index
						groups_new.append(
							XMLGroup(start_group, xml_list[start_group:end_group+1]))
						curr_line_start_group_index = curr_line_end_group_index+1
						break

			elif "<?xml" in xml_list[curr_line_start_group_index]:
				for curr_line_end_group_index in range(curr_line_start_group_index, len(xml_list)):
					if ">" in xml_list[curr_line_end_group_index]:
						end_group = curr_line_end_group_index
						groups_new.append(
							XMLGroup(start_group, xml_list[start_group:end_group+1]))
						curr_line_start_group_index = curr_line_end_group_index+1
						break

			else:
				groups_new.append(
					XMLLine(curr_line_start_group_index, xml_list[curr_line_start_group_index]))
				curr_line_start_group_index += 1

		return groups_new

	def generate_result_xml(self):
		pass

	def make_anchor_links(self, group_old, group_new):
		gray_lines_list = []

	def generate_struct(self):

		xml_1 = self.new_old_XML_groups
		xml_2 = self.new_new_XML_groups

		curr_new_xml_obj_index = 0

		new_obj_index = 0

		new_xml_1 = []
		new_xml_1_lines = 0
		new_xml_2 = []
		new_xml_2_lines = 0
		res_xml = []
		res_xml_lines = 0

		for old_obj_index in range(len(xml_1)):
			
			if type(xml_1[old_obj_index]) == XMLLine:

				curr_line = xml_1[old_obj_index]
				line_to_res_xml = copy.deepcopy(curr_line)				

				if type(xml_2[curr_new_xml_obj_index]) == XMLLine:

					if curr_line.raw_line.strip() == xml_2[curr_new_xml_obj_index].raw_line.strip():
						if curr_line.raw_line.strip() != "":
							line_to_res_xml.add_XML_class("EQUAL_IN_BOTH_XMLS_LINE")
						new_xml_1.append(curr_line)
						new_xml_2.append(xml_2[curr_new_xml_obj_index])
						res_xml.append(line_to_res_xml)
						
					else:

						# line_to_res_xml.add_XML_class("LINE_FROM_OLD_XML")
						new_xml_1.append(curr_line)
						new_xml_2.append(XMLGrayLine())
						res_xml.append(line_to_res_xml)

					new_xml_1_lines += 1
					new_xml_2_lines += 1
					res_xml_lines += 1

				else:

					line_to_res_xml.add_XML_class("LINE_FROM_OLD_XML")
					new_xml_1.append(curr_line)
					new_xml_2.append(XMLGrayLine())
					res_xml.append(line_to_res_xml)
				
					new_xml_1_lines += 1
					new_xml_2_lines += 1
					res_xml_lines += 1
			
			elif type(xml_1[old_obj_index]) == XMLGroup:

				curr_group = xml_1[old_obj_index]
				group_to_res_xml = copy.deepcopy(curr_group)
				group_to_res_xml.add_XML_class("LINE_FROM_OLD_XML")
				new_xml_1.append(curr_group)

				for i in range(curr_group.length()):
					new_xml_2.append(XMLGrayLine())
					new_xml_2_lines += 1

				res_xml.append(group_to_res_xml)

				new_xml_1_lines += curr_group.length()
				res_xml_lines += group_to_res_xml.length()
			
			elif type(xml_1[old_obj_index]) == Item:

				curr_item = xml_1[old_obj_index]
				this_item_in_new_xml  = [item for item in xml_2 if type(item) == Item and (item.name == curr_item.name or curr_item.image_path == item.image_path)]

				if this_item_in_new_xml:					

					found_item_index = xml_2.index(this_item_in_new_xml[0])
					#TODO here

					while curr_new_xml_obj_index < found_item_index:
						new_item = xml_2[curr_new_xml_obj_index]
						if type(new_item) == Item:
							new_item_in_old_xml  = [item for item in xml_1 if type(item) == Item and (item.name == new_item.name or new_item.image_path == item.image_path)]
							if new_item_in_old_xml:
								pass
							else:
								new_xml_2.append(new_item)
								new_xml_2_lines += new_item.length()
								spaces_prefix = curr_item.raw_lines[0].count(" ")*" "
								new_item_copy_to_res_xml = copy.deepcopy(new_item)
								new_item_copy_to_res_xml.add_XML_prefix(spaces_prefix)
								new_item_copy_to_res_xml.add_XML_class("LINE_FROM_NEW_XML")
								res_xml.append(new_item_copy_to_res_xml)
								res_xml_lines += new_item_copy_to_res_xml.length()
								for i in range(new_item.length()):
									new_xml_1.append(XMLGrayLine())
									new_xml_1_lines += 1
						elif type(new_item) == XMLLine:
							line_copy_to_res_xml = copy.deepcopy(new_item)
							if new_item.raw_line.strip() != "":								
								line_copy_to_res_xml.add_XML_class("REDLINE")
								
							res_xml.append(line_copy_to_res_xml)
							res_xml_lines += 1
							new_xml_2.append(new_item)
							new_xml_2_lines += 1
							new_xml_1.append(XMLGrayLine())
							new_xml_1_lines += 1


						curr_new_xml_obj_index+=1


					new_xml_1.append(curr_item)
					new_xml_1_lines += curr_item.length()

					new_item = this_item_in_new_xml[0]

					new_xml_2.append(new_item)
					new_xml_2_lines += new_item.length()

					res_item = curr_item.merge_with_new(new_item)
					res_xml_lines += curr_item.length()
					res_xml.append(res_item)
					curr_new_xml_obj_index = found_item_index+1
					while new_xml_1_lines < max(new_xml_1_lines, new_xml_2_lines, res_xml_lines):
						new_xml_1.append(XMLGrayLine())
						new_xml_1_lines += 1
					
					while new_xml_2_lines < max(new_xml_1_lines, new_xml_2_lines, res_xml_lines):
						new_xml_2.append(XMLGrayLine())
						new_xml_2_lines += 1

					while res_xml_lines < max(new_xml_1_lines, new_xml_2_lines, res_xml_lines):
						res_xml.append(XMLGrayLine())
						res_xml_lines += 1

				else:

					if curr_item.type == "passive":

						new_xml_1.append(curr_item)
						new_xml_1_lines += curr_item.length()

						for i in range(curr_item.length()):
							new_xml_2.append(XMLGrayLine())
							new_xml_2_lines += 1
						
							res_xml.append(XMLRedLine())
							res_xml_lines += 1



		for new_obj_index in range(len(xml_2)):
			curr_item = xml_2[new_obj_index]