"""
Interfaccia web Streamlit per il convertitore XDSL to PyAgrum.
"""

import streamlit as st
import tempfile
import os
from xdsl_converter import XDSLConverter

def main():
    """Funzione principale dell'applicazione Streamlit."""
    
    st.title("XDSL to PyAgrum Converter")
    
    st.write("""
    Questa applicazione converte file XDSL (GeNIe) in codice PyAgrum.
    Carica un file XDSL per iniziare la conversione.
    """)
    
    uploaded_file = st.file_uploader("Carica file XDSL", type=['xdsl'])
    
    if uploaded_file is not None:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xdsl') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            converter = XDSLConverter()
            converter.parse_xdsl(tmp_path)
            pyagrum_code = converter.generate_pyagrum_code()
            
            st.subheader("Codice PyAgrum Generato")
            st.code(pyagrum_code, language='python')
            
            if st.download_button(
                label="Scarica codice Python",
                data=pyagrum_code,
                file_name="network.py",
                mime="text/plain"
            ):
                st.success("File scaricato con successo!")
                
        except Exception as e:
            st.error(f"Errore durante la conversione: {str(e)}")
            
        finally:
            os.unlink(tmp_path)
    else:
        st.info("Carica un file XDSL per vedere il codice PyAgrum equivalente.")

if __name__ == "__main__":
    main()
