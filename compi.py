import re

# Definición de los tokens
tokens = [
    ("COMENTARIO", r'//.*|/\*[\s\S]*?\*/'),  
    ("CADENA", r'"[^"\\]*(?:\\.[^"\\]*)*"'),  
    ("PALABRA_CLAVE", r'\b(si|sino|mientras|para|retornar|entero|flotante|caracter|vacío|doble|def)\b'),  
    ("OPERADOR_RELACIONAL", r'==|!=|<=|>=|<|>'),  
    ("OPERADOR_LOGICO", r'\|\||&&|!'), 
    ("OPERADOR_ASIGNACION", r'\+=|\-=|\*=|/=|%=|\&=|\|=|\^='),  
    ("ASIGNACION", r'='), 
    ("OPERADOR", r'[+\-*/%]'),  
    ("IDENTIFICADOR", r'\b[a-zA-Z_][a-zA-Z_0-9]*\b'), 
    ("NUMERO", r'\b\d+(\.\d+)?\b'), 
    ("DELIMITADOR", r'[(){};,]'), 
    ("ESPACIO", r'\s+'),  
]

# Lexer
def lexer(code):
    position = 0
    tokens_found = []
    errors = []

    while position < len(code):
        match = None
        for token_type, pattern in tokens:
            regex = re.compile(pattern)
            match = regex.match(code, position)
            if match:
                text = match.group(0)
                if token_type != "ESPACIO":
                    tokens_found.append((token_type, text))
                position = match.end(0)
                break
        
        if not match:
            errors.append(f"Error: Carácter inesperado '{code[position]}' en posición {position}")
            position += 1  # Avanza un carácter para continuar analizando

    return tokens_found, errors

# Clases para el árbol sintáctico
class Nodo:
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor
        self.hijos = []

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

    def __repr__(self, nivel=0):
        ret = "  " * nivel + f"{self.tipo}: {self.valor}\n"
        for hijo in self.hijos:
            ret += hijo.__repr__(nivel + 1)
        return ret

# Parser
def parser(tokens):
    index = 0

    def parse_expresion():
        nonlocal index
        if index >= len(tokens):
            return None
        token_type, token_value = tokens[index]

        if token_type in ("IDENTIFICADOR", "NUMERO"):
            nodo = Nodo(token_type, token_value)
            index += 1
            return nodo
        elif token_type == "DELIMITADOR" and token_value == "(":
            index += 1
            nodo = parse_expresion()
            if tokens[index][1] != ")":
                raise SyntaxError("Se esperaba ')'")
            index += 1
            return nodo
        return None

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

code = input("Por favor, ingresa el código que deseas analizar:\n")

try:
    tokens_result, errors = lexer(code)
    print("\nTokens encontrados:")
    
    agrupados = {}
    
    for token in tokens_result:
        token_type, text = token
        if token_type in agrupados:
            agrupados[token_type] += " " + text
        else:
            agrupados[token_type] = text
    
    for token_type, texts in agrupados.items():
        print(f"{token_type}: {texts}")

    if errors:
        print("\nErrores encontrados:")
        for error in errors:
            print(error)

    # Generar el árbol sintáctico
    arbol = parser(tokens_result)
    print("\nÁrbol sintáctico:")
    print(arbol)

except SyntaxError as e:
    print(f"Error: {e}")
