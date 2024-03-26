#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import base64
import sys

HEADER = r"""<?xml version="1.0" encoding="UTF-8"?>
<quiz>

"""
END = r"""</quiz>
"""
QUESTION_TEMPLATE_PT1 = r"""	<question type="multichoice">
		<name>
			<text>QUESTION_NAME</text>
		</name>
		<questiontext format="html">
			<text><![CDATA[QUESTION_TEXT]]></text>
"""
BASE64_IMAGE_TEMPLATE = r"""			<file name="IMAGE_NAME" path="/" encoding="base64">BASE64_IMAGE_CONTENT</file>
"""
QUESTION_TEMPLATE_PT2 = r"""		</questiontext>
		<generalfeedback format="html">
			<text><![CDATA[GENERAL_FEEDBACK]]></text>
		</generalfeedback>
		<defaultgrade>1.0000000</defaultgrade>
		<penalty>0.3333333</penalty>
		<hidden>0</hidden>
		<idnumber></idnumber>
		<single>true</single>
		<shuffleanswers>true</shuffleanswers>
		<answernumbering>none</answernumbering>
		<showstandardinstruction>1</showstandardinstruction>
		<correctfeedback format="html">
			<text><![CDATA[<p>Vaš odgovor je točan.</p>]]></text>
		</correctfeedback>
		<partiallycorrectfeedback format="html">
			<text><![CDATA[<p>Vaš odgovor je djelomično točan.</p>]]></text>
		</partiallycorrectfeedback>
		<incorrectfeedback format="html">
			<text><![CDATA[<p>Vaš odgovor nije točan.</p>]]></text>
		</incorrectfeedback>
		<shownumcorrect/>
		<answer fraction="100" format="html">
			<text><![CDATA[<p>CORRECT_ANSWER</p>]]></text>
			<feedback format="html">
				<text></text>
			</feedback>
		</answer>
		<answer fraction="0" format="html">
			<text><![CDATA[<p>FALSE_ANSWER_1</p>]]></text>
			<feedback format="html">
				<text></text>
			</feedback>
		</answer>
		<answer fraction="0" format="html">
			<text><![CDATA[<p>FALSE_ANSWER_2</p>]]></text>
			<feedback format="html">
				<text></text>
			</feedback>
		</answer>
		<answer fraction="0" format="html">
			<text><![CDATA[<p>FALSE_ANSWER_3</p>]]></text>
			<feedback format="html">
				<text></text>
			</feedback>
		</answer>
	</question>

"""

QUESTION_TEMPLATE_PT2_EN = r"""		</questiontext>
		<generalfeedback format="html">
			<text><![CDATA[GENERAL_FEEDBACK]]></text>
		</generalfeedback>
		<defaultgrade>1.0000000</defaultgrade>
		<penalty>0.3333333</penalty>
		<hidden>0</hidden>
		<idnumber></idnumber>
		<single>true</single>
		<shuffleanswers>true</shuffleanswers>
		<answernumbering>none</answernumbering>
		<showstandardinstruction>1</showstandardinstruction>
		<correctfeedback format="html">
			<text><![CDATA[<p>Your answer is correct.</p>]]></text>
		</correctfeedback>
		<partiallycorrectfeedback format="html">
			<text><![CDATA[<p>Your answer is partially correct.</p>]]></text>
		</partiallycorrectfeedback>
		<incorrectfeedback format="html">
			<text><![CDATA[<p>Your answer is incorrect.</p>]]></text>
		</incorrectfeedback>
		<shownumcorrect/>
		<answer fraction="100" format="html">
			<text><![CDATA[<p>CORRECT_ANSWER</p>]]></text>
			<feedback format="html">
				<text></text>
			</feedback>
		</answer>
		<answer fraction="0" format="html">
			<text><![CDATA[<p>FALSE_ANSWER_1</p>]]></text>
			<feedback format="html">
				<text></text>
			</feedback>
		</answer>
		<answer fraction="0" format="html">
			<text><![CDATA[<p>FALSE_ANSWER_2</p>]]></text>
			<feedback format="html">
				<text></text>
			</feedback>
		</answer>
		<answer fraction="0" format="html">
			<text><![CDATA[<p>FALSE_ANSWER_3</p>]]></text>
			<feedback format="html">
				<text></text>
			</feedback>
		</answer>
	</question>

"""

def main(FILE, NEW_TEX_FILE, NEW_XML_FILE,EN):
	with open(FILE) as f:
		TEX = f.read()

	TEX = re.sub(r'(?<!\\)\$\$(.*?)(?<!\\)\$\$',r'\\[ \1 \\]', TEX, flags=re.S)
	TEX = re.sub(r'(?<!\\)\$(.*?)(?<!\\)\$',r'\\( \1 \\)', TEX)

	TEX = re.sub(r'<',r' < ', TEX)
	TEX = re.sub(r'>',r' > ', TEX)

	with open(NEW_TEX_FILE,'w') as f:
		f.write(TEX)

	matches = re.findall(r'\\begin\{problem\}\[(.*?)\](.*?)\\end\{problem\}', TEX, flags=re.S)

	OUTPUT = HEADER
	problems = []
	i=0
	for Ime_zadatka,problem_all in matches:
		i+=1
		options = re.findall(r'\\begin\{options\}.*?\\item(.*?)\\item(.*?)\\item(.*?)\\item(.*?)\\end\{options\}', problem_all, flags=re.S)[0]
		Answer1, Answer2, Answer3, Answer4 = options
		Slike = re.findall(r'\\begin\{slika\}.*?\\includegraphics\{(.*?)\}.*?\\end\{slika\}', problem_all, flags=re.S)

		Text_zadatka = r'<p>' + re.findall(r'(.*?)\\begin\{options\}', problem_all, flags=re.S)[0].strip() + r'</p>'
		Text_zadatka = re.sub(r'\\begin\{slika\}.*?\\includegraphics\{(.*?)\}.*?\\end\{slika\}', r'</p><p><img src="@@PLUGINFILE@@/\1"></p><p>', Text_zadatka, flags=re.S)
		
		Text_zadatka = re.sub(r'(\\\[.*?\\\])', r'</p><p>\1</p><p>', Text_zadatka, flags=re.S)
		Text_zadatka = re.sub(r'<p></p>', r'', Text_zadatka, flags=re.S)
		
		Feedback = r'<p>' + re.findall(r'\\begin\{feedback\}(.*?)\\end\{feedback\}', problem_all, flags=re.S)[0].strip() + r'</p>'
		Feedback = re.sub(r'(\\\[.*?\\\])', r'</p><p>\1</p><p>', Feedback, flags=re.S)
		Feedback = re.sub(r'<p></p>', r'', Feedback, flags=re.S)
		
		Ime_zadatka = Ime_zadatka.strip()
		Text_zadatka = Text_zadatka.strip()
		Answer1 = Answer1.strip()
		Answer2 = Answer2.strip()
		Answer3 = Answer3.strip()
		Answer4 = Answer4.strip()
		Feedback = Feedback.strip()

		problems.append(dict(Ime_zadatka=Ime_zadatka, Text_zadatka=Text_zadatka, Answers = [Answer1, Answer2, Answer3, Answer4], Feedback=Feedback))

		OUTPUT += r"""<!-- question: """ + str(i) + r"""	-->
		"""

		OUTPUT += QUESTION_TEMPLATE_PT1.replace('QUESTION_NAME', f'{i:03} {Ime_zadatka}').replace('QUESTION_TEXT', Text_zadatka)
		for slika in Slike:
			with open(slika, 'rb') as f:
				img64_data = base64.b64encode(f.read())
			OUTPUT += BASE64_IMAGE_TEMPLATE.replace('IMAGE_NAME', slika).replace('BASE64_IMAGE_CONTENT',img64_data.decode('utf-8'))

		if EN:
			OUTPUT += QUESTION_TEMPLATE_PT2_EN.replace('GENERAL_FEEDBACK', Feedback).replace('CORRECT_ANSWER', Answer1).replace('FALSE_ANSWER_1', Answer2).replace('FALSE_ANSWER_2', Answer3).replace('FALSE_ANSWER_3', Answer4)
		else:
			OUTPUT += QUESTION_TEMPLATE_PT2.replace('GENERAL_FEEDBACK', Feedback).replace('CORRECT_ANSWER', Answer1).replace('FALSE_ANSWER_1', Answer2).replace('FALSE_ANSWER_2', Answer3).replace('FALSE_ANSWER_3', Answer4)

	OUTPUT += END

	with open(NEW_XML_FILE,'w') as f:
		f.write(OUTPUT)


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print(f"Usage: {sys.argv[0]} <filename> [-e] [-F]")
		sys.exit(1)

	FILE = sys.argv[1]
	
	options = []
	for arg in sys.argv[2:]:
		if arg.startswith("-"):
			options.extend(arg[1:])

	if not os.path.exists(FILE):
		print(f"Error: File '{FILE}' not found.")
		sys.exit(1)
	
	NEW_TEX_FILE = os.path.splitext(FILE)[0] + '_new.tex'
	NEW_XML_FILE = os.path.splitext(FILE)[0] + '.xml'

	FORCE = 'F' in options
	EN = 'e' in options

	if os.path.exists(NEW_TEX_FILE) and not FORCE:
		print(f"Error: File '{NEW_TEX_FILE}' already exists.")
		sys.exit(1)

	if os.path.exists(NEW_XML_FILE) and not FORCE:
		print(f"Error: File '{NEW_XML_FILE}' already exists.")
		sys.exit(1)

	main(FILE, NEW_TEX_FILE, NEW_XML_FILE, EN)