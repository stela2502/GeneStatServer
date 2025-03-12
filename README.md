# GeneStatServer

GeneStatServer is a python module based on Flask that spans up a Flask server to analyze BED files and connect the bed entries to genes and further on to statistic values for these genes.

With the GeneStatsServer, users can analyze the effects of gene knockdowns on gene expression near specific genomic regions. For example, if you are studying the knockdown of GeneX — a gene known to bind to specific locations in the genome — you can upload a BED file that defines these binding sites and a GFT file that fits to the BED file. The server will then allow you to upload a statistical table which e.g. compares gene expression between wild-type (WT) cells and GeneX knockdown (KD) cells, identifying genes whose expression is affected by the knockdown. By focusing on genes that lie close to the genomic regions in the BED file, the server helps pinpoint which genes are most likely to be regulated by GeneX's binding activity. This tool provides an easy way to integrate genomic data with expression analysis, offering insights into the functional role of GeneX in your system.

# Install

Either from github:

```
pip install git+https://github.com/stela2502/GeneStatServer.git
```

or using pip (in the future)

```
pip install GeneStatsServer
```

# Usage

The package will start a Flask based server to interact with the database. The server will both create the path and the database file is not existing. Start from an not existing file!

```
GeneStatsServer /path/to/your/database.db
```

I hope the web interface is kind of self explanatory. Let's see if I get questions.

# Issuse

If you encounter problems with this software please create a new [Github Issue](https://github.com/stela2502/GeneStatServer/issues) - thank you for your interest!
