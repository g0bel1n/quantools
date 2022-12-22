<h1 align="center">
  <img alt="TinyAutoML Logo" src="images/logo_quantools.png" width="448px"/><br/>
</h1>


<p align="center">Quantools is a Python3.11 library for quantitative tasks </p>


<p align="center">
<a href="https://github.com/g0bel1n/quantools/actions/workflows/testing.yml" 
target="_blank"><img src="https://github.com/g0bel1n/quantools/actions/workflows/testing.yml/badge.svg" alt="Tests" /></a>
<img src="https://img.shields.io/github/license/g0bel1n/TinyAutoML?style=flat-square" alt="Licence MIT" />
<!-- <img src="https://img.shields.io/pypi/v/TinyAutoML?style=flat-square" alt="Pypi" /> -->
<img src="https://img.shields.io/github/repo-size/g0bel1N/quantools?style=flat-square" alt="Size" />
<img src="https://img.shields.io/github/commit-activity/m/g0bel1n/quantools?style=flat-square" alt="Commits" />
<a href="https://www.python.org/downloads/release/python-390/" 
target="_blank"><img src="https://img.shields.io/badge/python-3.9-blue.svg" alt="Python Version" /></a>
</p>

```python
import quantools as qt

X = qt.generate_brownian_returns(1, 1000, drift=0, vol=1e-2)

# X is a Table object

```

You can get some indicators:

```python
X.calmar(risk_free = .05)
X.sharpe()
X.cumulative()
...
```

You can plot the results :
```python
X.plot()
```
<h1 align="center">
  <img alt="plot" src="images/output.png" width="448px"/><br/>
</h1>


or autoplot it :

```python
X.autoplot()
```
<h1 align="center">
  <img alt="Autoplot" src="images/autoplot.png" width="448px"/><br/>
</h1>



You can transform your data:


```python

X.stationnarize(inplace=True) #Fractionnal differentiation
X.normalize()
```






## TODO : add test for plotting, sharpe, calmar etc 