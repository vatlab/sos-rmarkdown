[![Anaconda-Server Badge](https://anaconda.org/conda-forge/sos-rmarkdown/badges/version.svg)](https://anaconda.org/conda-forge/sos-rmarkdown)
[![PyPI version](https://badge.fury.io/py/sos-rmarkdown.svg)](https://badge.fury.io/py/sos-rmarkdown)
[![Build Status](https://travis-ci.org/vatlab/sos-rmarkdown.svg?branch=master)](https://travis-ci.org/vatlab/sos-rmarkdown)


# sos-rmarkdown

The RMarkdown format is a markdown format with embedded R expressions and code blocks, and is extremely popular for R users. SoS Notebook is an extension to Jupyter Notebook that allows the use of multiple kernels in one notebook, and enables RMarkdown-like features such as markdown text with inline expression and code blocks in multiple languages. `sos-rmarkdown` provides an almost lossless converter to convert Rmarkdown files to SoS notebooks using the `sos` file conversion mechanism.

## Installation

`sos-rmarkdown` and related tools ([`sos`](https://github.com/vatlab/sos), [`sos-notebook`](https://github.com/vatlab/sos-notebook), [`sos-r`](https://github.com/vatlab/sos-r), [`markdown-kernel`](https://github.com/vatlab/markdown-kernel), [`papermill`](https://github.com/nteract/papermill), [`sos-papermill`](https://github.com/vatlab/sos-papermill) etc) can be installed with command

```
pip install sos-rmarkdown
```

or

```
conda -c conda-forge sos-rmarkdown
```

if you are using a conda environment.


## Basic Usage

You can convert a Rmd file to a Jupyter notebook with command

```
sos convert input.Rmd output.ipynb
```

and optionally execute the resulting notebook with option `--execute`

```
sos convert input.Rmd output.ipynb --execute
```

The resulting notebook could be converted to HTML format using any of the jupyter or [SoS Notebook templates](https://github.com/vatlab/sos-notebook/tree/master/src/sos_notebook/templates) using commands such as

```
sos convert output.ipynb output.html --template sos-report-toc-v2
```

These steps could be combined with a `Rmd` -> `HTML` converter using the following command if you would only like to generate a SoS-style report from a Rmarkdown document:

```
sos convert input.rmd output.html --execute --template sos-report-toc-v2
```

## Features

Although there are already a number of Rmd to Jupyter converters such as [notedown](https://github.com/aaren/notedown), [RMD-to-Jupyter](https://github.com/lecy/RMD-to-Jupyter) (uses rpy2), they lack support for some of the Rmakdown features due to limitations of the Jupyter notebook platform. Fortunately, SoS Notebook, especially its Jupyter Lab extension addresses most of the limitations and offers an almost perfect conversion from R markdown to Jupyter notebook.

### Markdown text with inline expressions

Rmarkdown supports inline expressions, which are R expressions embedded in markdown texts. Jupyter cannot handle embedded expressions in its markdown cells because markdown cells are handled in its frontend and does not interact with the computing kernel. SoS Notebook addresses this problem with the use of a [markdown kernel](https://github.com/vatlab/markdown-kernel), which is essentially a markdown kernel 

For example, the following Rmarkdown text
```
I counted `r sum(c(1,2,3))` blue cars on the highway.
```
is converted to a markdown cell that is evaluated in a R kernel as follows

![image](https://user-images.githubusercontent.com/9889312/68706428-74504c80-0555-11ea-972e-26f80f1ef033.png)

### Code blocks in multiple languages

Code blocks in Rmarkdown supports [multiple languages](https://bookdown.org/yihui/rmarkdown/language-engines.html) such as Python, Julia, and Stata. A Jupyter notebook with an `ir` kernel can only evaluate R scripts, but a SoS Notebook can include multiple kernels in one notebook.

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

Note that SoS Notebook supports the [use of multiple kernels in one notebook](https://vatlab.github.io/blog/post/sos-notebook/) and allows data exchange between live kernels. This is differnt from Rmarkdown's multi-language approach and might lead to different results. For example, whereas multiple Python3 cells are always executed by the same Python kernel, RMarkdown's Python code blocks can be executed independently (if without `reticulate`).

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
