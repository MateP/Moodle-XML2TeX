#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import base64
import sys

TEX_BEGIN = r"""% !TeX encoding = UTF-8
% !TeX TS-program = pdflatex
% !TeX spellcheck = hr_HR
\documentclass[a4paper,11pt,oneside]{amsart}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}

\usepackage{graphicx}
\usepackage{amsthm}
\usepackage[margin=2cm]{geometry}

\title{KPZ 1}

\theoremstyle{definition}
\newtheorem{problem}{Zadatak}

\AtBeginEnvironment{problem}{\vspace{1ex}\begin{minipage}{.95\textwidth}}
\AtEndEnvironment{problem}{\end{minipage}\vspace{1ex}}

\newenvironment{feedback}{\it}{}
\newenvironment{options}{\begin{enumerate}}{\end{enumerate}}
\newenvironment{slika}{\begin{center}}{\end{center}}

\begin{document}
\vspace*{-10ex}
\maketitle
\begin{center}
\textbf{Točan odgovor MORA biti prvi (1) na listi!}
\end{center}
\bigskip
"""

TEX_PROBLEM_TEMPLATE = r"""
\begin{problem}[PROBLEM_NAME]
	PROBLEM_TEXT
	\begin{options}
OPTIONS
	\end{options}
	\begin{feedback}
		FEEDBACK
	\end{feedback}
\end{problem}
"""

IMG_TEMPLATE = r"""	\begin{slika}
		\includegraphics{\1}
	\end{slika}
"""

TEX_END = r"""\end{document}
"""

def main(XML_FILE, NEW_TEX_FILE):
	DIR = os.path.dirname(XML_FILE)

	with open(XML_FILE) as f:
		XML = f.read()

	matches = re.findall(r'\<question (.*?)\>(.*?)\<\/question\>', XML, flags=re.S)

	OUTPUT = TEX_BEGIN
	problems = []

	for match in matches:
		# OUTPUT += r"""
		# %%% """ + match[0] 

		question = match[1]

		name = re.findall(r'\<name\>.*?\<text\>(.*?)\<\/text\>.*?\<\/name\>', question, flags=re.S)[0]

		questiontext = re.findall(r'\<questiontext.*?\<text\>(.*?)\<\/text\>.*?\<\/questiontext\>', question, flags=re.S)[0]

		generalfeedback = re.findall(r'\<generalfeedback.*?\<text\>(.*?)\<\/text\>.*?\<\/generalfeedback\>', question, flags=re.S)[0]

		answers = re.findall(r'\<answer fraction="(.*?)".*?\<text\>(.*?)\<\/text\>.*?\<\/answer\>', question, flags=re.S)

		images = re.findall(r'\<file name="(.*?)".*?\>(.*?)\<\/file\>', question, flags=re.S)


		problems.append(dict(
			question_type = match[0],
			Ime_zadatka=name,
			Text_zadatka=questiontext,
			Answers = answers,
			Feedback=generalfeedback,
			Slike = images
			))

		for image_name, img64_data in images:
			with open(os.path.join(DIR,image_name),'wb') as img_file:
				img_file.write(base64.b64decode(img64_data))

		def strip(text):
			if '![CDATA[' in text:
				text = re.sub(r'\<!\[CDATA\[(.*?)\]\]\>', r'\1', text, flags=re.S)
				
				text = re.sub(r'&lt;', r' < ', text, flags=re.S)
				text = re.sub(r'&gt;', r' > ', text, flags=re.S)
				text = re.sub(r'\<br\>', r'', text, flags=re.S)
				text = re.sub(r'\\\&nbsp\;', r'', text, flags=re.S)
				text = re.sub(r'\&nbsp\;', r'', text, flags=re.S)
				text = re.sub(r'\<span.*?\>(.*?)\</span\>', r'\1', text, flags=re.S)

			return re.sub(r'\<p\>(.*?)\<\/p\>', r'\1', text, flags=re.S)

		problem_text = strip(questiontext)

		problem_text = re.sub(r'\<img.*?src=.*?\/(.*?)\".*?\>', r"\t\\begin{slika}\n\t\t\\includegraphics{\1}\n\t\\end{slika}\n'", problem_text, flags=re.S)

		options_list = []

		for pts, ans in answers:
			if int(float(pts)) == 100:
				options_list.insert(0, r'		\item ' + strip(ans) )
			else:
				options_list.append(r'		\item ' + strip(ans))

		options = '\n'.join(options_list)


		OUTPUT += TEX_PROBLEM_TEMPLATE.replace('PROBLEM_NAME', strip(name)).replace('FEEDBACK', strip(generalfeedback)).replace('PROBLEM_TEXT', problem_text).replace('OPTIONS', options)

	OUTPUT += TEX_END

	with open(NEW_TEX_FILE,'w') as f:
		f.write(OUTPUT)


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print(f"Usage: {sys.argv[0]} <filename> [-F]")
		sys.exit(1)

	XML_FILE = sys.argv[1]

	options = []
	for arg in sys.argv[2:]:
		if arg.startswith("-"):
			options.extend(arg[1:])

	if not os.path.exists(XML_FILE):
		print(f"Error: File '{XML_FILE}' not found.")
		sys.exit(1)
	
	NEW_TEX_FILE = os.path.splitext(XML_FILE)[0] + '.tex'

	FORCE = 'F' in options

	if os.path.exists(NEW_TEX_FILE) and not FORCE:
		print(f"Error: File '{NEW_TEX_FILE}' already exists.")
		sys.exit(1)

	main(XML_FILE, NEW_TEX_FILE)