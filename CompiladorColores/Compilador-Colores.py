import ply.lex as lex
import ply.yacc as yacc
import tkinter as tk
import os
import subprocess
from webcolors import rgb_to_name


codigo_intermedio = """
#include <stdio.h>

int main() {\n
"""
directorio_actual = os.path.dirname(os.path.abspath(__file__))
archivo_intermedio = "intermedio.c"

ruta_archivo_c = os.path.join(directorio_actual, archivo_intermedio)

resultado_sintaxis=[]

tokens = (
    'ID',
    'NUMERO',
    'MAS',
    'MENOS',
    'POR',
    'IGUAL',
    'STRING',
    'ROJO',
    'IPARE',
    'DPARE',
    'AZUL',
    'VERDE',
    'COMIENZO',
    'FINAL',
    'CORCHDE',
    'CORCHIZ',
    'COLOR1',
    'COLOR2',
    'COMBINACION',
    'IMPRIMIR',
    'COMENTARIO',
    'COMA'
)

t_MAS = r'\+'
t_MENOS = r'-'
t_POR = r'\*'
t_IGUAL = r'\='
t_IPARE = r'\('  
t_DPARE = r'\)' 
t_CORCHDE = r'\}'  
t_CORCHIZ = r'\{' 
t_COMA = r'\,' 

def t_STRING(t):
    r'\"(\d+|[^\"]*)\"'  
    t.value = t.value[1:-1]  
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value == 'COMIENZO':
        t.type = 'COMIENZO'
    elif t.value == 'FINAL':
        t.type = 'FINAL'
        return t
    elif t.value == 'COLOR1':
        t.type = 'COLOR1'
        return t
    elif t.value == 'COLOR2':
        t.type = 'COLOR2'
        return t
    elif t.value == 'ROJO':
        t.type = 'ROJO'
        return t
    elif t.value == 'VERDE':
        t.type = 'VERDE'
        return t
    elif t.value == 'AZUL':
        t.type = 'AZUL'
        return t
    elif t.value == 'COMBINACION':
        t.type = 'COMBINACION'
        return t
    elif t.value == 'IMPRIMIR':
        t.type = 'IMPRIMIR'
        return t
    return t

def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_COMENTARIO(t):
    r'>>.*'
    pass  

t_ignore = ' \t\n'

def t_error(t):
    print("Carácter no válido '%s'" % t.value[0])
    t.lexer.skip(1)

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def es_entero(valor):
    try:
        int(valor)
        return True
    except ValueError:
        return False
    
precedence = (
    ('right', 'IGUAL'),
    ('left', 'MAS', 'MENOS'),
    ('left', 'POR')
)

def p_programa(p):
    '''
    programa : COMIENZO CORCHIZ declaraciones CORCHDE FINAL
    '''
    p[0] = p[3]

def p_declaraciones(p):
    '''
    declaraciones : declaraciones declaracion
                  | declaracion
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_instrucciones(p):
    '''
    instrucciones : instruccion
                  | instrucciones instruccion
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_instruccion(p):
    '''
    instruccion : asignacion
                | impresion
    '''
    pass

def p_asignacion(p):
    '''
    declaracion : ID IGUAL NUMERO
                | ID IGUAL STRING
    '''
    if isinstance(p[3], int):
        p[0] = tabla_simbolos[p[1]] = int(p[3])
    else:
        if es_entero(p[3]):
            p[0] = tabla_simbolos[p[1]] = int(p[3])
        else:
            p[0] = tabla_simbolos[p[1]] = p[3]
   
    global codigo_intermedio
    codigo_intermedio += f"int {p[1]}{p[2]}{p[3]};\n"

def p_statement_read(p):
    '''
    asignacion : ID
    '''
    try:
        value = tabla_simbolos[p[1]]
        print(value)
    except KeyError:
        print("Error: El identificador", p[1], "no está definido.")

def p_statement_print(p):
    '''
    impresion : IMPRIMIR
    '''
    try:
        value = tabla_combinacion["COMBINACION"]
        print(value)
    except KeyError:
        print("Error: El identificador", p[1], "no está definido.")

def p_numero(p):
    '''
    numero : NUMERO
           | ID
    '''
    p[0] = p[1]

def p_operador(p):
    ''' 
    operador : MAS
             | MENOS
             | POR
    '''
    p[0]=p[1]


def p_colors(p):
    '''
    colors : COLOR1
           | COLOR2
    '''
    p[0] = p[1]

def p_asignacioncolor(p):
    '''
    declaracion : colors IGUAL IPARE ROJO IGUAL numero COMA VERDE IGUAL numero COMA AZUL IGUAL numero DPARE
    '''
    valores = []
    for i in [6, 10, 14]:
        if isinstance(p[i], int):
         valores.append(int(p[i]))
        elif isinstance(tabla_simbolos[p[i]], int):
            valores.append(int(tabla_simbolos[p[i]]))
        else:
         raise ValueError("El valor no es un entero ni está en la tabla de símbolos")
    valor, valor2, valor3 = valores
   
    def validar_valor_color(valor, nombre):
        if valor < 0 or valor > 255:
            raise ValueError(f"Valor {nombre} fuera de rango")
        
    validar_valor_color(valor, "ROJO")
    validar_valor_color(valor2, "VERDE")
    validar_valor_color(valor3, "AZUL")
    
    tabla_combinacion[p[1]] = (valor,valor2,valor3)
    p[0]=tabla_combinacion[p[1]]
   
    global codigo_intermedio

    if p[1] == "COLOR1":
        codigo_intermedio += f"int {p[1]}[3];\nint t1 = {p[6]};\nint t2 = {p[10]};\nint t3 = {p[14]};\n"
        codigo_intermedio += f"{p[1]}[0] = t1;\n{p[1]}[1] = t2;\n{p[1]}[2] = t3;\n"
    else :
        codigo_intermedio += f"int {p[1]}[3];\nint t4 = {p[6]};\nint t5 = {p[10]};\nint t6 = {p[14]};\n"
        codigo_intermedio += f"{p[1]}[0] = t4;\n{p[1]}[1] = t5;\n{p[1]}[2] = t6;\n"


def p_sumacolores(p):
    '''
    declaracion : COMBINACION IGUAL IPARE colors operador colors DPARE
    '''
    def sumar_colores(c1, c2):
        r = min(c1[0] + c2[0], 255)
        g = min(c1[1] + c2[1], 255)
        b = min(c1[2] + c2[2], 255)
        return (r, g, b)
    
    def restar_colores(c1, c2):
        r = min(c1[0] - c2[0], 255)
        g = min(c1[1] - c2[1], 255)
        b = min(c1[2] - c2[2], 255)
        return (r, g, b)
    
    def multiplicar_colores(c1, c2):
        r = min(c1[0] * c2[0], 255)
        g = min(c1[1] * c2[1], 255)
        b = min(c1[2] * c2[2], 255)
        return (r, g, b)
    valor1=tabla_combinacion[p[4]][0]
    valor2=tabla_combinacion[p[4]][1]
    valor3=tabla_combinacion[p[4]][2]
    valor4=tabla_combinacion[p[6]][0]
    valor5=tabla_combinacion[p[6]][1]
    valor6=tabla_combinacion[p[6]][2]
    
    c1=(int(valor1),int(valor2),int(valor3))
    c2=(int(valor4),int(valor5),int(valor6))

    def operar_colores(p35, c1, c2):
        if p35=="+":
                return sumar_colores(c1, c2)
        elif p35=="-":
                return restar_colores(c1,c2)
        elif p35=="*":
                return multiplicar_colores(c1,c2)
        else:
            return None
    tabla_combinacion[p[1]] = operar_colores(p[5],c1,c2)
    p[0]=operar_colores(p[5],c1,c2)
    global codigo_intermedio
    codigo_intermedio += f"int {p[1]}[3];\n"
    codigo_intermedio += f"""
        for (int i = 0; i < 3; ++i) {{
            COMBINACION[i] = COLOR1[i]{p[5]}COLOR2[i];
        if (COMBINACION[i] > 255) {{
        COMBINACION[i] = 255;
        }} else if (COMBINACION[i] < 0) {{
        COMBINACION[i] = 0;
        }}
    }}
"""
  

def p_expresiones_varias(p):
    '''
    expvarias : COLOR1
                | COLOR2
                | COMBINACION
                | NUMERO
                | ID
    '''
    p[0] = p[1]

def p_imprimir(p):
    '''
    declaracion : IMPRIMIR IGUAL COMBINACION
                | IMPRIMIR IGUAL colors
                | IMPRIMIR IGUAL numero
                | IMPRIMIR IGUAL STRING MAS expvarias
    '''
    global codigo_intermedio
    if p[3] == 'COMBINACION':
        rgb_color=(tabla_combinacion['COMBINACION'])
        try:
            color_name = rgb_to_name(rgb_color)
            p[0] = color_name
            codigo_intermedio += "printf(\"Color Combinado: (%d, %d, %d)\\n\",COMBINACION[0],COMBINACION[1],COMBINACION[2]);\n"
            codigo_intermedio += f'printf("{color_name}");\n'
        except ValueError:
            p[0] = "Color Desconocido"
            codigo_intermedio += f'printf("{p[0]}");\n'
    elif p[3]=='COLOR1' or p[3]=='COLOR2':
        rgb_color=(tabla_combinacion[p[3]])
        try:
            color_name = rgb_to_name(rgb_color)
            p[0]= color_name
            codigo_intermedio += f'printf("El color seleccionado es: (%d, %d, %d)\\n\",{p[3]}[0],{p[3]}[1],{p[3]}[2]);\n'
            codigo_intermedio += f'printf("{color_name}");\n'
        except ValueError:
            p[0] = "Color desconocido"
            codigo_intermedio += f'printf("{p[0]}");\n'
    elif p[3] in tabla_simbolos:
        p[0] = tabla_simbolos[p[3]]
        codigo_intermedio += f'printf("%d", {p[0]});\n'
    elif isinstance(p[3],int):
        p[0] = p[3]
        codigo_intermedio += f'printf("%d", {p[0]});\n'
    elif p[4]=='+':
        if p[5] == 'COMBINACION':
            rgb_color=(tabla_combinacion['COMBINACION'])
            try:
                color_name = rgb_to_name(rgb_color)
                p[0]= p[3] + color_name
                codigo_intermedio += "printf(\"Color Combinado: (%d, %d, %d)\\n\",COMBINACION[0],COMBINACION[1],COMBINACION[2]);\n"
                codigo_intermedio += f'printf("{p[3]}{color_name}");\n'
            except ValueError:
                p[0]= p[3] + "Color Desconocido"
        elif p[5] == "COLOR1" or p[5]=="COLOR2" :
            rgb_color=(tabla_combinacion[p[5]])
            try:
                color_name = rgb_to_name(rgb_color)
                p[0]= p[3] + color_name
                codigo_intermedio += "printf(\"Color Combinado: (%d, %d, %d)\\n\",COMBINACION[0],COMBINACION[1],COMBINACION[2]);\n"
                codigo_intermedio += f'printf("{p[3]}{color_name}");\n'
            except ValueError:
                p[0]= p[3] + "Color Desconocido"
                codigo_intermedio += f'printf("{p[0]}");\n'
        elif p[5] in tabla_simbolos:
            p[0] = p[3] + str(tabla_simbolos[p[5]])
            codigo_intermedio += "printf(\"Color Combinado: (%d, %d, %d)\\n\",COMBINACION[0],COMBINACION[1],COMBINACION[2]);\n"
            codigo_intermedio += f'printf("{p[3]}%d", {tabla_simbolos[p[5]]});\n'
        else:
            p[0] = str(p[3]) + str(p[5])
            codigo_intermedio += "printf(\"Color Combinado: (%d, %d, %d)\\n\",COMBINACION[0],COMBINACION[1],COMBINACION[2]);\n"
            codigo_intermedio += f'printf("{p[3]}%s", "{p[5]}");\n'
    else:
        p[0] = "valor no encontrado"
    codigo_intermedio += "getchar();\n}"


    
def guardar_intermedio():
    global codigo_intermedio
    try:
        with open(ruta_archivo_c, 'w') as file:
            file.truncate(0)
            file.write(codigo_intermedio)
            codigo_intermedio = ""
    except Exception as e:
        print("Error al guardar el código intermedio:", str(e))


def p_error(p):
    global resultado_sintaxis
    resultado_sintaxis.clear()
    if p:
        generateExec_button.config(state=tk.DISABLED)  # Deshabilita el botón
        resultado = "Error Sintactico de {} en el valor {}".format(str(p.type),str(p.value))
        sintactico_label.insert(tk.END, f"Resultado del análisis: {resultado}\n")
    else:
        generateExec_button.config(state=tk.DISABLED)  # Deshabilita el botón
        resultado = "Error Sintactico {}".format(p)
        sintactico_label.insert(tk.END, f"Resultado del análisis: {resultado}\n")
    resultado_sintaxis.append(resultado)

tabla_simbolos = {}

tabla_combinacion = {}

lexer = lex.lex()

def analizador_lexico():
    code = code_entry.get("1.0", tk.END)
    
    output_text.delete("1.0", tk.END)

    lexer.input(code)
  
    for token in lexer:
        output_text.insert(tk.END, f"Token: {token.type}, Valor: {token.value}\n")
        
parser = yacc.yacc()

def analizador_sintactico():
    code = code_entry.get("1.0", tk.END)
    
    sintactico_label.delete("1.0", tk.END)

    try:
        generateExec_button.config(state=tk.NORMAL)
        result = parser.parse(code, lexer=lexer)
        sintactico_label.insert(tk.END, f"Resultado del análisis: {result}\n")
    except Exception as e:
        generateExec_button.config(state=tk.DISABLED) 
        sintactico_label.insert(tk.END, f"Error: {e}\n")
    
def analizar_codigo():
    analizador_lexico()
    analizador_sintactico()
    guardar_intermedio()
    ejecutable_label.config(text="Estado de Ejecutable: -")

def generateExecute():

    nombre_ejecutable = "Compilador de Colores"
    nombre_objeto = "objeto.o"
    ruta_objeto = os.path.join(directorio_actual, nombre_objeto)
    ruta_ejecutable = os.path.join(directorio_actual, nombre_ejecutable)
    
    subprocess.run(["gcc", "-c", ruta_archivo_c, "-o", ruta_objeto])
    subprocess.run(["gcc", ruta_archivo_c, "-o", ruta_ejecutable])
    ejecutable_label.config(text="Estado de Ejecutable: Generado")
    global codigo_intermedio
    codigo_intermedio = """
    #include <stdio.h>

    int main() {\n
    """



window = tk.Tk()
window.title("Compilador de Colores")
window.geometry("1400x780")
window.configure(bg="light gray")

code_label = tk.Label(window, text="Introduce el código:")
code_label.place(x=320, y=70, anchor="s")

code_entry = tk.Text(window, height=35)
code_entry.pack(side=tk.LEFT, padx=40)
code_entry.insert('end', 'COMIENZO{\nCOLOR1=(ROJO=254,VERDE=254,AZUL=254)\nCOLOR2=(ROJO=1,VERDE=1,AZUL=1)\nCOMBINACION=(COLOR1+COLOR2)\nIMPRIMIR=COMBINACION\n}FINAL')

analyze_button = tk.Button(window, text="Analizar código", command=analizar_codigo)
analyze_button.place(x=280, y=710, anchor="s")

generateExec_button = tk.Button(window, text="Generar Ejecutable", command=generateExecute)
generateExec_button.place(x=400, y=710, anchor="s")
generateExec_button.config(state=tk.DISABLED)

output_label = tk.Label(window, text="Analizador Léxico:")
output_label.pack()

output_text = tk.Text(window, height=20)
output_text.pack()

separator = tk.Frame(window, width=2, bd=1, relief=tk.SUNKEN)
separator.pack(fill=tk.Y, padx=5, pady=5)

sintactico_label = tk.Label(window, text="Analizador Sintáctico:")
sintactico_label.pack()

sintactico_label = tk.Text(window, height=20)
sintactico_label.pack()

separator2 = tk.Frame(window, width=2, bd=2, relief=tk.SUNKEN)
separator2.pack(fill=tk.Y, padx=5, pady=5)

ejecutable_label = tk.Label(window, text="Estado de Ejecutable: -")
ejecutable_label.pack()


window.mainloop()