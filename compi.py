import re
import tkinter as tk
from tkinter import simpledialog
import graphviz as gv
import os

# Nodo para representar el árbol sintáctico
class Nodo:
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor
        self.hijos = []

    def agregar_hijo(self, nodo):
        self.hijos.append(nodo)

    def __repr__(self, nivel=0):
        ret = "\t" * nivel + repr((self.tipo, self.valor)) + "\n"
        for hijo in self.hijos:
            ret += hijo.__repr__(nivel + 1)
        return ret

import re

# Lexer básico actualizado
def lexer(code):
    tokens = [
        ("PALABRA_CLAVE", r'\b(int|float|char|if|else|while|for|return)\b'),
        ("IDENTIFICADOR", r'[a-zA-Z_]\w*'),
        ("NUMERO", r'\d+(\.\d+)?'),  # Soporta números decimales
        ("ASIGNACION", r'='),
        ("OPERADOR", r'[+\-*/%]'),  # Incluye operador de módulo %
        ("DELIMITADOR", r'[();{},]'),
        ("CADENA", r'\".*?\"'),  # Soporta cadenas entre comillas dobles
        ("COMENTARIO", r'//.*?$|/\*.*?\*/'),  # Comentarios de línea y bloque
        ("ESPACIO", r'\s+')
    ]

    tokens_found = []
    position = 0
    while position < len(code):
        match = None
        for token_type, pattern in tokens:
            regex = re.compile(pattern)
            match = regex.match(code, position)
            if match:
                text = match.group(0)
                if token_type != "ESPACIO":  # Ignorar espacios
                    tokens_found.append((token_type, text))
                position = match.end(0)
                break
        if not match:
            # Mostrar token problemático y contexto
            context = code[position:position+10]  # Mostrar los siguientes 10 caracteres
            print(f"Error: Token no reconocido en la posición {position}. Contexto: '{context}'")
            raise SyntaxError(f"Token no reconocido en la posición {position}")
    return tokens_found



# Parser
def parser(tokens):
    if not tokens:
        return None
    index = 0

    def parse_expresion():
        nonlocal index
        nodo = Nodo("Expresión", "")
        
        while index < len(tokens):
            token_type, token_value = tokens[index]
            if token_type == "IDENTIFICADOR" or token_type == "NUMERO":
                hijo = Nodo(token_type, token_value)
                nodo.agregar_hijo(hijo)
                index += 1
            elif token_type == "OPERADOR":
                hijo = Nodo("Operador", token_value)
                nodo.agregar_hijo(hijo)
                index += 1
            elif token_type == "DELIMITADOR":
                if token_value in (';', '{', '}'):
                    break
        return nodo

    def parse_asignacion():
        nonlocal index
        if tokens[index][0] == "IDENTIFICADOR":
            nodo = Nodo("Asignación", tokens[index][1])
            index += 1
            if tokens[index][0] == "ASIGNACION":
                index += 1
                hijo_exp = parse_expresion()
                nodo.agregar_hijo(hijo_exp)
            return nodo
        return None

    raiz = Nodo("Programa", "")
    while index < len(tokens):
        if tokens[index][0] == "PALABRA_CLAVE":
            nodo = Nodo("Declaración", tokens[index][1])
            index += 1
            if tokens[index][0] == "IDENTIFICADOR":
                nodo.agregar_hijo(Nodo("IDENTIFICADOR", tokens[index][1]))
                index += 1
                if tokens[index][0] == "ASIGNACION":
                    index += 1
                    hijo_exp = parse_expresion()
                    nodo.agregar_hijo(hijo_exp)
            raiz.agregar_hijo(nodo)
        elif tokens[index][0] == "IDENTIFICADOR":
            nodo = parse_asignacion()
            if nodo:
                raiz.agregar_hijo(nodo)
        elif tokens[index][0] == "DELIMITADOR" and tokens[index][1] == ";":
            index += 1
        else:
            index += 1

    return raiz

# Función para generar el gráfico usando Graphviz
def generar_arbol_sintactico(raiz):
    def recorrer_arbol(nodo, parent_id, dot, node_count):
        current_id = f'node{node_count[0]}'
        label = f"{nodo.tipo}: {nodo.valor}"
        dot.node(current_id, label, shape='circle')  # Nodo circular
        if parent_id:
            dot.edge(parent_id, current_id)  # Conexión entre nodos
        node_count[0] += 1

        for hijo in nodo.hijos:
            recorrer_arbol(hijo, current_id, dot, node_count)

    dot = gv.Digraph(comment="Árbol Sintáctico")
    node_count = [0]
    recorrer_arbol(raiz, None, dot, node_count)
    return dot

# Función para pedir el código al usuario y generar el árbol
def analizar_codigo():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de Tkinter
    codigo = simpledialog.askstring("Entrada de código", "Introduce el código a analizar:")
    
    if not codigo:
        print("No se ha proporcionado código para analizar.")
        return

    # Proceso completo: tokenizar, parsear y generar el árbol gráfico
    try:
        tokens = lexer(codigo)
        arbol = parser(tokens)
        
        # Generar y renderizar el árbol sintáctico
        dot = generar_arbol_sintactico(arbol)
        
        # Guardar el archivo en formato PNG y mostrar el gráfico
        filename = 'arbol_sintactico'
        dot.render(filename, format='png')  # Generar imagen PNG
        print(f"Árbol sintáctico generado y guardado como '{filename}.png'.")

        # Abrir la imagen generada automáticamente (en caso de sistemas operativos compatibles)
        if os.name == 'nt':  # Para Windows
            os.startfile(f"{filename}.png")
        elif os.name == 'posix':  # Para sistemas tipo Unix
            os.system(f"xdg-open {filename}.png")
    except SyntaxError as e:
        print(f"Error de sintaxis durante el análisis: {e}")

# Llamar a la función para iniciar el proceso
analizar_codigo()
    
