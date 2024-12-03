"""
XDSL to PyAgrum Converter
------------------------
Modulo principale per la conversione di file XDSL in codice PyAgrum.
"""

import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import pyAgrum as gum

class NodeFactory:
    """Factory per la creazione di nodi nel diagramma di influenza."""
    
    @staticmethod
    def create_node(network: gum.InfluenceDiagram, node_type: str, node_id: str, 
                   states: List[str]) -> int:
        """
        Crea un nuovo nodo nel diagramma.
        
        Args:
            network: Il diagramma di influenza
            node_type: Tipo di nodo ('cpt', 'decision', 'utility')
            node_id: Identificatore del nodo
            states: Stati possibili del nodo
            
        Returns:
            int: ID del nodo creato
        """
        var = gum.LabelizedVariable(node_id, node_id, 
                                  states if node_type != 'utility' else 1)
        
        if node_type == 'cpt':
            return network.addChanceNode(var)
        elif node_type == 'decision':
            return network.addDecisionNode(var)
        elif node_type == 'utility':
            return network.addUtilityNode(var)
        else:
            raise ValueError(f"Tipo di nodo non supportato: {node_type}")

class CodeGenerator(ABC):
    """Interfaccia base per i generatori di codice."""
    
    @abstractmethod
    def generate(self, network: gum.InfluenceDiagram, nodes: Dict[str, int],
                utilities: Dict[str, ET.Element]) -> str:
        """Genera il codice per il network."""
        pass

class PyAgrumCodeGenerator(CodeGenerator):
    """Generatore di codice PyAgrum."""
    
    def generate(self, network: gum.InfluenceDiagram, nodes: Dict[str, int],
                utilities: Dict[str, ET.Element]) -> str:
        """
        Genera il codice PyAgrum per il network.
        
        Args:
            network: Il diagramma di influenza
            nodes: Dizionario dei nodi
            utilities: Dizionario dei nodi utilità
            
        Returns:
            str: Codice PyAgrum generato
        """
        code = [
            "import pyAgrum as gum",
            "",
            "# Creazione del diagramma di influenza",
            "diag = gum.InfluenceDiagram()",
            ""
        ]
        
        # Genera codice per nodi chance
        self._generate_chance_nodes(network, nodes, code)
        
        # Genera codice per nodi decisione
        self._generate_decision_nodes(network, nodes, code)
        
        # Genera codice per archi
        self._generate_arcs(network, code)
        
        # Genera codice per CPT
        self._generate_cpts(network, nodes, code)
        
        # Genera codice per nodi utilità
        self._generate_utility_nodes(network, nodes, code)
        
        return "\n".join(code)
    
    def _generate_chance_nodes(self, network: gum.InfluenceDiagram, 
                             nodes: Dict[str, int], code: List[str]) -> None:
        """Genera il codice per i nodi chance."""
        for node_id, node in nodes.items():
            if network.isChanceNode(node):
                var = network.variable(node)
                states = [f'"{s}"' for s in var.labels()]
                code.extend([
                    f"# Creazione del nodo {node_id}",
                    f"{node_id} = diag.addChanceNode(gum.LabelizedVariable('{node_id}', "
                    f"'{node_id}', {states}))",
                    ""
                ])
    
    def _generate_decision_nodes(self, network: gum.InfluenceDiagram,
                               nodes: Dict[str, int], code: List[str]) -> None:
        """Genera il codice per i nodi decisione."""
        for node_id, node in nodes.items():
            if network.isDecisionNode(node):
                var = network.variable(node)
                states = [f'"{s}"' for s in var.labels()]
                code.extend([
                    f"# Creazione del nodo decisione {node_id}",
                    f"{node_id} = diag.addDecisionNode(gum.LabelizedVariable('{node_id}', "
                    f"'{node_id}', {states}))",
                    ""
                ])
    
    def _generate_arcs(self, network: gum.InfluenceDiagram, code: List[str]) -> None:
        """Genera il codice per gli archi."""
        code.append("# Aggiunta degli archi")
        for arc in network.arcs():
            parent = network.variable(arc[0]).name()
            child = network.variable(arc[1]).name()
            code.append(f"diag.addArc({parent}, {child})")
        code.append("")
    
    def _generate_cpts(self, network: gum.InfluenceDiagram,
                      nodes: Dict[str, int], code: List[str]) -> None:
        """Genera il codice per le CPT."""
        code.append("# Definizione delle probabilità condizionate")
        for node_id, node in nodes.items():
            if network.isChanceNode(node):
                probs = network.cpt(node).tolist()
                if probs:
                    code.append(f"diag.cpt({node_id}).fillWith({probs})")
        code.append("")
    
    def _generate_utility_nodes(self, network: gum.InfluenceDiagram,
                              nodes: Dict[str, int], code: List[str]) -> None:
        """Genera il codice per i nodi utilità."""
        for node_id, node in nodes.items():
            if network.isUtilityNode(node):
                code.extend([
                    f"# Creazione del nodo utilità {node_id}",
                    f"{node_id} = diag.addUtilityNode(gum.LabelizedVariable('{node_id}', "
                    f"'{node_id}', 1))",
                    f"diag.utility({node_id}).fillWith({network.utility(node).tolist()})",
                    ""
                ])

class XDSLConverter:
    """Classe principale per la conversione di file XDSL in PyAgrum."""
    
    def __init__(self, code_generator: Optional[CodeGenerator] = None):
        """
        Inizializza il convertitore.
        
        Args:
            code_generator: Generatore di codice da utilizzare
        """
        self.network = None
        self.nodes: Dict[str, int] = {}
        self.utilities: Dict[str, ET.Element] = {}
        self.weights: Dict[str, float] = {}
        self.code_generator = code_generator or PyAgrumCodeGenerator()
    
    def parse_xdsl(self, file_path: str) -> gum.InfluenceDiagram:
        """
        Parsa il file XDSL e crea il diagramma di influenza.
        
        Args:
            file_path: Percorso del file XDSL
            
        Returns:
            gum.InfluenceDiagram: Il diagramma di influenza creato
            
        Raises:
            ValueError: Se la struttura del file XDSL non è valida
        """
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        smile_nodes = root.find('.//nodes')
        if smile_nodes is None:
            raise ValueError("Struttura XDSL non valida: elemento 'nodes' non trovato")
        
        self.network = gum.InfluenceDiagram()
        
        # Prima passata: crea tutti i nodi
        for node in smile_nodes:
            self._create_node(node)
            
        # Seconda passata: aggiungi archi e probabilità
        for node in smile_nodes:
            self._add_arcs_and_probabilities(node)
            
        return self.network
    
    def _create_node(self, node: ET.Element) -> None:
        """
        Crea un nodo nel diagramma.
        
        Args:
            node: Elemento XML rappresentante il nodo
        """
        node_id = node.get('id')
        if node_id is None:
            return
            
        states = [state.get('id') for state in node.findall('state')]
        
        if node.tag in ['cpt', 'decision', 'utility']:
            self.nodes[node_id] = NodeFactory.create_node(
                self.network, node.tag, node_id, states
            )
            if node.tag == 'utility':
                self.utilities[node_id] = node
        elif node.tag == 'mau':
            self._process_mau_node(node)
    
    def _process_mau_node(self, node: ET.Element) -> None:
        """
        Processa un nodo MAU (Multi-Attribute Utility).
        
        Args:
            node: Elemento XML rappresentante il nodo MAU
        """
        parents_elem = node.find('parents')
        weights_elem = node.find('weights')
        if parents_elem is not None and weights_elem is not None:
            parents = parents_elem.text.split() if parents_elem.text else []
            weights = weights_elem.text.split() if weights_elem.text else []
            self.weights = {
                parent: float(weight) 
                for parent, weight in zip(parents, weights)
            }
    
    def _add_arcs_and_probabilities(self, node: ET.Element) -> None:
        """
        Aggiunge archi e probabilità al nodo.
        
        Args:
            node: Elemento XML rappresentante il nodo
        """
        node_id = node.get('id')
        if node_id not in self.nodes:
            return
            
        self._add_arcs(node, node_id)
        self._add_probabilities(node, node_id)
    
    def _add_arcs(self, node: ET.Element, node_id: str) -> None:
        """
        Aggiunge gli archi al nodo.
        
        Args:
            node: Elemento XML rappresentante il nodo
            node_id: ID del nodo
        """
        parents_elem = node.find('parents')
        if parents_elem is not None and parents_elem.text:
            parent_nodes = parents_elem.text.split()
            for parent in parent_nodes:
                if parent in self.nodes:
                    self.network.addArc(self.nodes[parent], self.nodes[node_id])
    
    def _add_probabilities(self, node: ET.Element, node_id: str) -> None:
        """
        Aggiunge probabilità o utilità al nodo.
        
        Args:
            node: Elemento XML rappresentante il nodo
            node_id: ID del nodo
        """
        if node.tag == 'cpt':
            probs_elem = node.find('probabilities')
            if probs_elem is not None and probs_elem.text:
                prob_values = [float(p) for p in probs_elem.text.split()]
                self.network.cpt(self.nodes[node_id]).fillWith(prob_values)
        elif node.tag == 'utility':
            utils_elem = node.find('utilities')
            if utils_elem is not None and utils_elem.text:
                util_values = [
                    float(u) * self.weights.get(node_id, 1) 
                    for u in utils_elem.text.split()
                ]
                self.network.utility(self.nodes[node_id]).fillWith(util_values)
    
    def generate_pyagrum_code(self) -> str:
        """
        Genera il codice PyAgrum equivalente.
        
        Returns:
            str: Il codice PyAgrum generato
        """
        if not self.network:
            return "# Nessun network da convertire"
            
        return self.code_generator.generate(self.network, self.nodes, self.utilities)
