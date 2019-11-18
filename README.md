[![Anaconda-Server Badge](https://anaconda.org/conda-forge/sos-rmarkdown/badges/version.svg)](https://anaconda.org/conda-forge/sos-rmarkdown)
[![PyPI version](https://badge.fury.io/py/sos-rmarkdown.svg)](https://badge.fury.io/py/sos-rmarkdown)
[![Build Status](https://travis-ci.org/vatlab/sos-rmarkdown.svg?branch=master)](https://travis-ci.org/vatlab/sos-rmarkdown)


# sos-rmarkdown

The [RMarkdown format](https://rmarkdown.rstudio.com/) is a markdown format with embedded R expressions and code blocks, and is extremely popular for R users. [SoS Notebook](https://github.com/vatlab/sos-notebook/) is an extension to Jupyter Notebook that allows the use of multiple kernels in one notebook, and enables RMarkdown-like features such as markdown text with inline expressions and code blocks in multiple languages. `sos-rmarkdown` is an extension module to [SoS Workflow System and Polyglot Notebook](https://vatlab.github.io/sos-docs/) and provides an almost lossless converter from Rmarkdown files to SoS notebooks using the `sos` file conversion mechanism.

## Installation

`sos-rmarkdown` and related tools ([`sos`](https://github.com/vatlab/sos), [`sos-notebook`](https://github.com/vatlab/sos-notebook), [`sos-r`](https://github.com/vatlab/sos-r), [`markdown-kernel`](https://github.com/vatlab/markdown-kernel), [`papermill`](https://github.com/nteract/papermill), [`sos-papermill`](https://github.com/vatlab/sos-papermill)) can be installed with command

```
pip install sos-rmarkdown
```

or

```
conda -c conda-forge sos-rmarkdown
```

if you are using a conda environment. Note that 

1. The conda installation of `sos-r` will install the conda version of `R` (e.g. [`r-base`](https://anaconda.org/conda-forge/r-base)).

2. You will need to install additional kernels and language modules such as [`sos-python`](https://github.com/vatlab/sos-python) and [`sos-bash`](https://github.com/vatlab/sos-bash) if the Rmarkdown documents use these languages.



## Basic Usage

You can convert a `.Rmd` file to a Jupyter notebook with command

```
sos convert input.Rmd output.ipynb
```

and optionally execute the resulting notebook with option `--execute`

```
sos convert input.Rmd output.ipynb --execute
```

The resulting notebook could be converted to a HTML format using any of the jupyter or [SoS Notebook templates](https://github.com/vatlab/sos-notebook/tree/master/src/sos_notebook/templates) using commands such as

```
sos convert output.ipynb output.html --template sos-report-toc-v2
```

These steps could be combined with a `Rmd` -> `HTML` converter using the following command if you would only like to execute a Rmarkdown document with SoS Notebook, not knitr, and generate a SoS-style report:

```
sos convert input.rmd output.html --execute --template sos-report-toc-v2
```

Note that the `--execute` option essentially uses [`sos-papermill`](https://github.com/vatlab/sos-papermill) to execute the notebook with an SoS kernel. You can execute the notebook directly with command `papermill --engine sos` if you would like to use advanced features of [papermill](https://github.com/nteract/papermill).

## Features

Although there are already a number of Rmd to Jupyter converters such as [notedown](https://github.com/aaren/notedown), [RMD-to-Jupyter](https://github.com/lecy/RMD-to-Jupyter), [ipymd](https://github.com/chronitis/ipyrmd), and [rmd2jupyter](https://github.com/mkearney/rmd2jupyter), they lack support for some of the Rmakdown features due to limitations of the Jupyter notebook platform. SoS Notebook, especially its Jupyter Lab extension addresses most of the limitations and offers an almost perfect conversion from R markdown to Jupyter notebook.

### Markdown text with inline expressions

Rmarkdown supports inline expressions, which are R expressions embedded in markdown texts. Jupyter cannot handle embedded expressions in its markdown cells because markdown cells are handled in its frontend and do not interact with the computing kernel. SoS Notebook addresses this problem with the use of a [markdown kernel](https://github.com/vatlab/markdown-kernel), which is essentially a markdown kernel that can be expanded with language-specific inline expressions.

For example, the following Rmarkdown text
```
I counted `r sum(c(1,2,3))` blue cars on the highway.
```
is converted to a markdown cell that is evaluated in a R kernel as follows

![image](https://user-images.githubusercontent.com/9889312/68706428-74504c80-0555-11ea-972e-26f80f1ef033.png)

### Code blocks in multiple languages

Code blocks in Rmarkdown supports [multiple languages](https://bookdown.org/yihui/rmarkdown/language-engines.html) such as Python, Julia, and Stata. A Jupyter notebook with an `ir` kernel can only evaluate R scripts, and the use of magics such as `%%python` is rather limiting. SoS Notebook supports the [use of multiple kernels in one notebook](https://vatlab.github.io/blog/post/sos-notebook/) and can accommodate code blocks in multiple languages. 

For example, code blocks such as

````
```{python}
def f(x):
  return x + 2
f(2)
```
````
and

````
```{r engine="python"}
def f(x):
  return x + 2
f(2)
```
````

are converted to cells with approprivate kernels such as

![image](https://user-images.githubusercontent.com/9889312/68706553-a792db80-0555-11ea-92e8-633a75b36894.png)

Note that SoS Notebook supports the execution of multiple kernels and allows data exchange between live kernels. This is differnt from Rmarkdown's multi-language approach and might lead to different results. For example, whereas multiple Python3 cells are always executed by the same Python kernel (unless multiple Python kernels are used with a `%use` magic or the Python kernel is restarted with a `%shutdown -r` magic), RMarkdown's Python code blocks can be executed together or independently (with or without `reticulate`).

### Hiding input and/or output of code blocks

Rmarkdown's code blocks accept options such as `echo=FALSE` and `include=FALSE` which controls the output of input and/or output of code blocks. There were no corresponding features for classic Jupyter Notebook but Jupyter Lab supports hiding of input and/or output of cells using cell metadata. The `sos-rmarkdown` converter understands these options and converts code blocks such as,

````
```{r echo=FALSE}
arr <- rnorm(5)
cat(arr)
```
````

with appropriate open/colapse status

![image](https://user-images.githubusercontent.com/9889312/68706480-8df19400-0555-11ea-891c-dff0e455e039.png)

In addition, whereas the default templates from `jupyter nbconvert` does not respect the collasping status of cells and renders input and output of all cells, SoS Notebook provides templates that supports these features. For example, template `sos-report-toc-v2` outputs all cells but hides collapsed inputs and outputs by default. The hidden content could be displayed by selecting a dropdown box to the top right corner of the document. Please refer to [SoS Notebook templates](https://github.com/vatlab/sos-notebook/tree/master/src/sos_notebook/templates) for a list of templates.

## Conversion from SoS Notebook to RMarkdown?

`sos-rmarkdown` is designed to convert Rmarkdown documents to Jupyter notebooks. It aims to provide a lossless converter from RMarkdown to SoS Notebook so please [submit a ticket](https://github.com/vatlab/sos-rmarkdown/issues) if certain features of RMarkdown are not properly converted.

`sos-rmarkdown` does retain all global and code block options of RMarkdown documents as global and cell meta data in the resulting notebooks, but a SoS Notebook to RMarkdown converter is not planned. Please submit a PR if you are interested in adding this feature.
