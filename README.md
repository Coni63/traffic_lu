# Info Traffic - Selenium

This repository contains a script to extract data from [https://www2.pch.etat.lu/comptage/home.jsf](https://www2.pch.etat.lu/comptage/home.jsf). This website provides the count of vehicules in some points of the Luxembourg with hourly measures. There is 2 kinds of vehicules:

- Voitures : vehicule shorter than 8.6m
- Utilitaires : vehicule longer that 8.6m 

## Installation

### Setup the environment

First, create in the virtual environment called `venv` and install all libraries in `environment.yml` with:

```
conda create env -f environment.yml
```
### Install the driver for Selenium

This code has been prepared for Firefox but you can change it easily in `script.py:199`. The instruction to install the driver is available at [https://selenium-python.readthedocs.io/installation.html#drivers](https://selenium-python.readthedocs.io/installation.html#drivers)

## Run the script

The script extract all measures available for a given date. If the date is not provided, if uses yesterday's date

```console
activate ./venv
python script.py --date 15/05/2020
```
The output will be saved in this folder and named `extract_15052020.csv`.

**IMPORTANT** : the date format must be `%d/%m/%Y`.

