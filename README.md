# XDSL to PyAgrum Converter

## Descrizione
XDSL to PyAgrum Converter è una libreria Python specializzata nella conversione di reti bayesiane e diagrammi di influenza dal formato XDSL (utilizzato da software come GeNIe) al formato PyAgrum. Questo strumento facilita la migrazione e l'interoperabilità tra diversi framework di modellazione probabilistica.

## TODO 

[ ] Supporto a Reti Bayesiane dinamiche

## Caratteristiche Principali
- Conversione accurata di reti bayesiane dal formato XDSL a PyAgrum
- Supporto completo per diagrammi di influenza
- Preservazione di strutture, probabilità e utilità
- Interfaccia web integrata tramite Streamlit
- API Python semplice e intuitiva

## Requisiti
- Python ≥ 3.8
- pyAgrum
- streamlit
- xml.etree.ElementTree (libreria standard Python)

## Installazione
```bash
pip install xdsl-converter
```

## Utilizzo

### Come Libreria Python
```python
from xdsl_converter import XDSLConverter

converter = XDSLConverter()

converter.parse_xdsl("path/to/network.xdsl")

pyagrum_code = converter.generate_pyagrum_code()

with open("network.py", "w") as f:
    f.write(pyagrum_code)
```

### Interfaccia Web
```bash
streamlit run app.py
```
