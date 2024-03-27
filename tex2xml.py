#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import base64
import sys
import lxml.etree as et


def question_element(count, Ime_zadatka, Text_zadatka, Slike, Feedback, Answers, EN):
	question = et.Element('question', type="multichoice")


	name = et.Element('name')
	text = et.Element('text')
	text.text = f'{count:03} {Ime_zadatka}'
	name.append(text)

	question.append(name)


	questiontext = et.Element('questiontext', format="html")
	text = et.Element('text')
	text.text = et.CDATA(Text_zadatka)
	questiontext.append(text)

	for slika in Slike:
		with open(slika, 'rb') as f:
			img64_data = base64.b64encode(f.read())

			file = et.Element('file', name=f"{slika}", path="/", encoding="base64")
			file.text = img64_data
			questiontext.append(file)

	question.append(questiontext)


	generalfeedback = et.Element('generalfeedback', format="html")
	text = et.Element('text')
	text.text = et.CDATA(Feedback)
	generalfeedback.append(text)

	question.append(generalfeedback)

	defaultgrade = et.Element('defaultgrade')
	defaultgrade.text = '1.0000000'
	question.append(defaultgrade)

	penalty = et.Element('penalty')
	penalty.text = '0.3333333'
	question.append(penalty)

	hidden = et.Element('hidden')
	hidden.text = '0'
	question.append(hidden)

	question.append(et.Element('idnumber'))

	single = et.Element('single')
	single.text = 'true'
	question.append(single)

	shuffleanswers = et.Element('shuffleanswers')
	shuffleanswers.text = 'true'
	question.append(shuffleanswers)

	answernumbering = et.Element('answernumbering')
	answernumbering.text = 'none'
	question.append(answernumbering)

	showstandardinstruction = et.Element('showstandardinstruction')
	showstandardinstruction.text = '1'
	question.append(showstandardinstruction)

	correctfeedback = et.Element('correctfeedback', format="html")
	text = et.Element('text')
	if EN:
		text.text = et.CDATA('<p>Your answer is correct.</p>')
	else:
		text.text = et.CDATA('<p>Vaš odgovor je točan.</p>')
	correctfeedback.append(text)
	question.append(correctfeedback)

	partiallycorrectfeedback = et.Element('partiallycorrectfeedback', format="html")
	text = et.Element('text')
	if EN:
		text.text = et.CDATA('<p>Your answer is partially correct.</p>')
	else:
		text.text = et.CDATA('<p>Vaš odgovor je djelomično točan.</p>')
	partiallycorrectfeedback.append(text)
	question.append(partiallycorrectfeedback)

	incorrectfeedback = et.Element('incorrectfeedback', format="html")
	text = et.Element('text')
	if EN:
		text.text = et.CDATA('<p>Your answer is incorrect.</p>')
	else:
		text.text = et.CDATA('<p>Vaš odgovor nije točan.</p>')
	incorrectfeedback.append(text)
	question.append(incorrectfeedback)

	question.append(et.Element('shownumcorrect'))

	answer = et.Element('answer', fraction="100", format="html")
	text = et.Element('text')
	text.text = et.CDATA(f'<p>{Answers[0]}</p>')
	answer.append(text)
	feedback = et.Element('feedback', format="html")
	text = et.Element('text')
	feedback.append(text)
	answer.append(feedback)
	question.append(answer)


	for ans in Answers[1:]:
		answer = et.Element('answer', fraction="0", format="html")
		text = et.Element('text')
		text.text = et.CDATA(f'<p>{ans}</p>')
		answer.append(text)
		feedback = et.Element('feedback', format="html")
		text = et.Element('text')
		feedback.append(text)
		answer.append(feedback)
		question.append(answer)


	return question


def main(TEX_FILE, NEW_TEX_FILE, NEW_XML_FILE,EN):
	with open(TEX_FILE) as f:
		TEX = f.read()

	TEX = re.sub(r'(?<!\\)\$\$(.*?)(?<!\\)\$\$',r'\\[ \1 \\]', TEX, flags=re.S)
	TEX = re.sub(r'(?<!\\)\$(.*?)(?<!\\)\$',r'\\( \1 \\)', TEX)

	TEX = re.sub(r'<',r' < ', TEX)
	TEX = re.sub(r'>',r' > ', TEX)

	with open(NEW_TEX_FILE,'w') as f:
		f.write(TEX)

	matches = re.findall(r'\\begin\{problem\}\[(.*?)\](.*?)\\end\{problem\}', TEX, flags=re.S)

	root = et.Element('quiz')

	problems = []
	i=0
	for Ime_zadatka,problem_all in matches:
		i+=1
		options_env = re.findall(r'\\begin\{options\}(.*?)\\end\{options\}', problem_all, flags=re.S)[0]
		options = [opt.strip() for opt in options_env.split('\\item') if opt.strip() != '']
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
		Answers = [ans.strip() for ans in options]
		Feedback = Feedback.strip()

		problems.append(dict(Ime_zadatka=Ime_zadatka, Text_zadatka=Text_zadatka, Answers = Answers, Feedback=Feedback))

		root.append(et.Comment(f'question: {i:03}'))

		root.append(question_element(i, Ime_zadatka, Text_zadatka, Slike, Feedback, Answers, EN))

	T = et.ElementTree(root)
	T.write(NEW_XML_FILE,encoding='utf-8',xml_declaration=True, pretty_print=True)


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print(f"Usage: {sys.argv[0]} <filename> [-e] [-F]")
		sys.exit(1)

	TEX_FILE = sys.argv[1]
	
	options = []
	for arg in sys.argv[2:]:
		if arg.startswith("-"):
			options.extend(arg[1:])

	if not os.path.exists(TEX_FILE):
		print(f"Error: File '{TEX_FILE}' not found.")
		sys.exit(1)
	
	NEW_TEX_FILE = os.path.splitext(TEX_FILE)[0] + '_new.tex'
	NEW_XML_FILE = os.path.splitext(TEX_FILE)[0] + '.xml'

	FORCE = 'F' in options
	EN = 'e' in options

	if os.path.exists(NEW_TEX_FILE) and not FORCE:
		print(f"Error: File '{NEW_TEX_FILE}' already exists.")
		sys.exit(1)

	if os.path.exists(NEW_XML_FILE) and not FORCE:
		print(f"Error: File '{NEW_XML_FILE}' already exists.")
		sys.exit(1)

	main(TEX_FILE, NEW_TEX_FILE, NEW_XML_FILE, EN)