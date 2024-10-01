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
                    if tokens_found and tokens_found[-1][0] == token_type:
                        tokens_found[-1] = (token_type, tokens_found[-1][1] + text)
                    else:
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

# Parser (muy básico)
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
                index += 1
            else:
                break

        return nodo

    raiz = Nodo("Programa", "")
    while index < len(tokens):
        raiz.agregar_hijo(parse_expresion())

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
