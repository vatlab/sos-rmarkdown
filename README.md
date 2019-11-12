[![Anaconda-Server Badge](https://anaconda.org/conda-forge/sos-rmarkdown/badges/version.svg)](https://anaconda.org/conda-forge/sos-rmarkdown)
[![PyPI version](https://badge.fury.io/py/sos-rmarkdown.svg)](https://badge.fury.io/py/sos-rmarkdown)
[![Build Status](https://travis-ci.org/vatlab/sos-rmarkdown.svg?branch=master)](https://travis-ci.org/vatlab/sos-rmarkdown)


# sos-rmarkdown

The RMarkdown format is a markdown format with embedded R expressions and code blocks, and is extremely popular for R users. The `sos-rmarkdown` module provides converters to convert Rmarkdown files to SoS notebooks using the `sos` converter mechanism.

## Installation

You can install `sos-rmarkdown` and related tools (`sos-notebook`, `papermill`, `sos-papermill` etc) with command

```
pip install sos-rmarkdown
```

or

```
conda -c conda-forge sos-rmarkdown
```

if you are using a conda environment.


## Basic Usage

You can convert a Rmd file with command

```
sos convert input.Rmd output.ipynb
```

and optionally execute the resulting notebook with option `--execute`

```
sos convert input.Rmd output.ipynb --execute
```

If you would like to further convert the Jupyter notebooks to HTML format, you can use commands

```
sos convert output.ipynb output.html --template sos-report-toc-v2
```

You can combine the two steps with commands such as

```
sos convert input.rmd output.html --execute --template sos-report-toc-v2
```

## Features

Although there are already a number of Rmd to Jupyter converters (e.g. [notedown](https://github.com/aaren/notedown), [RMD-to-Jupyter](https://github.com/lecy/RMD-to-Jupyter) (uses rpy2)), they lack support for some of the Rmakdown features due to limitations of the Jupyter notebook platform. Fortunately, SoS Notebook, especially its Jupyter Lab extension addresses most of the limitations and offers an almost perfect conversion from R markdown to Jupyter notebook.


The first Rmarkdown feature that is difficult to convert is its inline expressions, which are R expressions embedded in markdown texts. Jupyter cannot handle embedded expressions in its markdown cells because markdown cells are handled in its frontend and does not interact with the computing kernel. SoS Notebook addresses this problem with the use of a [markdown kernel](https://github.com/vatlab/markdown-kernel), which is essentially a markdown kernel 

For example, the following Rmarkdown text
```
I counted `r sum(c(1,2,3))` blue cars on the highway.
```
is converted to a markdown cell that is evaluated in a R kernel as follows

![image](https://user-images.githubusercontent.com/9889312/68706428-74504c80-0555-11ea-972e-26f80f1ef033.png)

The second Rmarkdown feature is its support for multiple languages, which allows it to have [code blocks in a number of langauges](https://bookdown.org/yihui/rmarkdown/language-engines.html). A Jupyter notebook with an `ir` kernel can only evaluate R scripts, but a SoS Notebook is able to include multiple kernels in one notebook.

For example, code blocks such as
```{python}
def f(x):
  return x + 2
f(2)
```

and

```{r engine="python"}
def f(x):
  return x + 2
f(2)
```

are converted to cells with approprivate kernels such as

![image](https://user-images.githubusercontent.com/9889312/68706553-a792db80-0555-11ea-92e8-633a75b36894.png)

in a separate `Python3` kernel.


The last feature that is not properly supported are options such as `echo=FALSE` and `include=FALSE` for Rmarkdown code blocks. There were no corresponding features for classic Jupyter Notebook but Jupyter Lab supports hiding of input and/or output of cells. Using these features, code blocks such as the following are converted as collapsed input and/or outputs,

```{r echo=FALSE}
arr <- rnorm(5)
cat(arr)
```

![image](https://user-images.githubusercontent.com/9889312/68706480-8df19400-0555-11ea-891c-dff0e455e039.png)

A related problem is that `jupyter nbconvert` does not respect the collasping status of cells and renders input and output of all cells. SoS Notebook addresses this problem by providing templates that honor the show/hide status of cells. For example, template `sos-report-toc-v2` outputs all cells but hides collapsed inputs and outputs by default. The hidden content could be displayed by selecting a dropdown box to the top right corner of the document.
