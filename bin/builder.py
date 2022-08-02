#!/usr/bin/python

import os

input_dirs = ['source/']

build_dir = 'build/'
OUTPUT_FILE = f'{build_dir}makefile.generated'

JOB = "\n\t"
TARGET = "\n"

######################################################################

def generate_file_tree(input_dir):
    targets = []

    for dirname, dirnames, filenames in os.walk(input_dir):
        for filename in filenames:
            source = os.path.join(dirname, filename)
            target = os.path.join('build/', filename).rsplit('.',1)[0]
            shortcut = filename.rsplit('.',1)[0]

            if source.rsplit('.', 1)[1] != "tmpl":
                targets.append((source, target, shortcut))

    return targets

def generate_converters(input_dir, output_dir):
    tex_converter = (
        f"{JOB}@$(LATEXCMD) $< >$@" + JOB
    ) + "@echo [rst2latex]: created '$@'"

    html_converter = (
        f"{JOB}@$(HTMLCMD) $< >$@" + JOB
    ) + "@echo [rst2html]: created '$@'"


    return (
        TARGET
        + output_dir
        + "%.tex"
        + ":"
        + input_dir
        + "%.rst"
        + tex_converter
        + TARGET
        + output_dir
        + "%.tex"
        + ":"
        + input_dir
        + "%.txt"
        + tex_converter
        + TARGET
        + output_dir
        + "%.html"
        + ":"
        + input_dir
        + "%.rst"
        + html_converter
        + TARGET
        + output_dir
        + "%.html"
        + ":"
        + input_dir
        + "%.txt"
        + html_converter
    )

def generate_builders(output_dir):
    return (
        TARGET
        + output_dir
        + "%.pdf"
        + ":"
        + output_dir
        + "%.tex"
        + JOB
        + "@$(PDFCMD) '$<' >|$@.log"
        + JOB
        + "@echo [pdflatex]: \(1/3\) built '$@'"
        + JOB
        + "@$(PDFCMD) '$<' >>$@.log"
        + JOB
        + "@echo [pdflatex]: \(2/3\) built '$@'"
        + JOB
        + "@$(PDFCMD) '$<' >>$@.log"
        + JOB
        + "@echo [pdflatex]: \(3/3\) built '$@'"
        + JOB
        + "@echo [PDF]: see '$@.log' for a full report of the pdf build process."
    )

def build_latex_targets(source, target):
    intermediate = target.rsplit('.',1)[0] + ".tex"

    return (
        TARGET
        + target
        + ".pdf"
        + ':'
        + source
        + TARGET
        + intermediate
        + ":"
        + source
    )

def build_html_targets(source, target):
    return f"{target}.html:{source}"

def build_shortcut_targets(target, shortcut):
    return f'{shortcut}:{target}.html {target}.pdf'

######################################################################

class GeneratedMakefile(object):
    def __init__(self):

        self.converters = []
        self.targets = []

        self.builder = generate_builders(build_dir)

        self.converters.extend(
            generate_converters(dir, build_dir) for dir in input_dirs
        )

        for dir in input_dirs:
            for (src, trg, shc) in generate_file_tree(dir):
                self.targets.append(build_latex_targets(src, trg))
                self.targets.append(build_html_targets(src, trg))
                self.targets.append(build_shortcut_targets(trg, shc))

makefile = GeneratedMakefile()

########################################################################

def main():
    with open(OUTPUT_FILE, "w") as output:
        for line in makefile.converters:
            output.write(line)

        output.write(makefile.builder)
        output.write('\n\n')

        for line in makefile.targets:
            output.write(line)
            output.write('\n')

if __name__ == "__main__":
    main()
