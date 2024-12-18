import sys
import ply.lex as lex
import ply.yacc as yacc
import yaml

# Лексические токены
tokens = (
    'IDENTIFIER',
    'NUMBER',
    'STRING',
    'CONST',
    'ASSIGN',
    'SEMICOLON',
    'LBRACE',
    'RBRACE',
    'COMMA',
    'QEXPR',
    'COMMENT',
)

t_ASSIGN = r'='
t_SEMICOLON = r';'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_ignore = ' \t'

# Обработка комментариев
def t_COMMENT(t):
    r'\!.*'
    pass

def t_CONST(t):
    r'const'
    return t

def t_QEXPR(t):
    r'\?\[[a-zA-Z][a-zA-Z0-9]*\]'
    t.value = t.value[2:-1]  # Извлекаем имя константы
    return t

def t_STRING(t):
    r'@\"([^\\\"]|\\.)*\"'
    t.value = t.value[2:-1]  # Убираем @" и "
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Недопустимый символ '{t.value[0]}' на строке {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

# Глобальная таблица констант
constants = {}

# Грамматика
def p_program(p):
    '''program : statements'''
    p[0] = {}
    for item in p[1]:
        if isinstance(item, dict):
            p[0].update(item)

def p_statements(p):
    '''statements : statements statement
                  | statement'''
    if len(p) == 3:
        p[0] = p[1]
        if p[2]:
            p[0].append(p[2])
    else:
        p[0] = [p[1]]

def p_statement(p):
    '''statement : const_statement
                 | expression'''
    p[0] = p[1]

def p_const_statement(p):
    '''const_statement : CONST IDENTIFIER ASSIGN value SEMICOLON'''
    constants[p[2]] = p[4]
    p[0] = None

def p_expression(p):
    '''expression : value'''
    p[0] = p[1]

def p_value(p):
    '''value : NUMBER
             | STRING
             | dictionary
             | QEXPR'''
    if p.slice[1].type == 'QEXPR':
        const_name = p[1]
        if const_name in constants:
            p[0] = constants[const_name]
        else:
            print(f"Ошибка: неопределенная константа '{const_name}'")
            p[0] = None
    else:
        p[0] = p[1]

def p_dictionary(p):
    '''dictionary : LBRACE items RBRACE'''
    p[0] = p[2]

def p_items(p):
    '''items : items item
             | item
             | empty'''
    if len(p) == 3:
        p[0] = p[1]
        if p[2]:
            p[0].update(p[2])
    elif len(p) == 2:
        p[0] = p[1] if p[1] else {}
    else:
        p[0] = {}

def p_item(p):
    '''item : IDENTIFIER ASSIGN value COMMA
            | IDENTIFIER ASSIGN value'''
    p[0] = {p[1]: p[3]}

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    if p:
        print(f"Синтаксическая ошибка возле '{p.value}' на строке {p.lineno}")
    else:
        print("Синтаксическая ошибка в конце файла")

parser = yacc.yacc()

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            input_text = f.read()
    else:
        print("Интерактивный ввод. Введите строки текста. Для завершения введите 'exit'.")
        lines = []
        while True:
            line = input(">>> ")  # Подсказка ввода
            if line.strip().lower() == "exit":
                break
            lines.append(line)
        input_text = "\n".join(lines)
    result = parser.parse(input_text)
    if result:
        yaml_output = yaml.dump(result, allow_unicode=True, default_flow_style=False, sort_keys=False)
        print(yaml_output)

if __name__ == '__main__':
    main()
