"""Content builder for board game prototypes.

Builds the JSON content pack injected into the board game engine.
Supports domains: matematica, ciencias, linguagem, historia, generico.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Question banks per domain
# ---------------------------------------------------------------------------

_MATEMATICA_QUESTIONS = [
    {"q": "Quanto é 1/2 + 1/4?", "options": ["3/4", "1/2", "1/3", "2/6"], "answer": 0, "bloom": 3, "category": "frações"},
    {"q": "Qual fração é equivalente a 2/4?", "options": ["1/2", "1/3", "3/4", "2/3"], "answer": 0, "bloom": 2, "category": "frações"},
    {"q": "Quanto é 3/4 - 1/4?", "options": ["1/2", "2/4", "1/4", "3/8"], "answer": 0, "bloom": 3, "category": "frações"},
    {"q": "Qual é maior: 2/3 ou 3/4?", "options": ["3/4", "2/3", "São iguais", "Depende"], "answer": 0, "bloom": 4, "category": "frações"},
    {"q": "Quanto é 1/3 + 1/3?", "options": ["2/3", "2/6", "1/6", "1/2"], "answer": 0, "bloom": 3, "category": "frações"},
    {"q": "Qual é a forma decimal de 1/4?", "options": ["0,25", "0,5", "0,75", "0,2"], "answer": 0, "bloom": 1, "category": "frações"},
    {"q": "Qual operação é a inversa da multiplicação?", "options": ["Divisão", "Subtração", "Adição", "Potenciação"], "answer": 0, "bloom": 1, "category": "aritmética"},
    {"q": "Quanto é 15 × 4?", "options": ["60", "55", "64", "56"], "answer": 0, "bloom": 3, "category": "aritmética"},
    {"q": "Quanto é 144 ÷ 12?", "options": ["12", "11", "13", "10"], "answer": 0, "bloom": 3, "category": "aritmética"},
    {"q": "Qual é o MMC de 4 e 6?", "options": ["12", "24", "6", "8"], "answer": 0, "bloom": 3, "category": "aritmética"},
    {"q": "Qual é o MDC de 12 e 18?", "options": ["6", "3", "9", "12"], "answer": 0, "bloom": 3, "category": "aritmética"},
    {"q": "Quanto é 2³?", "options": ["8", "6", "9", "16"], "answer": 0, "bloom": 1, "category": "potências"},
    {"q": "Qual é a raiz quadrada de 81?", "options": ["9", "8", "7", "10"], "answer": 0, "bloom": 1, "category": "aritmética"},
    {"q": "Quanto é 50% de 200?", "options": ["100", "50", "150", "25"], "answer": 0, "bloom": 3, "category": "porcentagem"},
    {"q": "Quanto é 25% de 80?", "options": ["20", "25", "15", "40"], "answer": 0, "bloom": 3, "category": "porcentagem"},
    {"q": "Qual é a fórmula da área do retângulo?", "options": ["base × altura", "base + altura", "2×(base+altura)", "base²"], "answer": 0, "bloom": 1, "category": "geometria"},
    {"q": "Qual é o perímetro de um quadrado de lado 5?", "options": ["20", "25", "10", "15"], "answer": 0, "bloom": 3, "category": "geometria"},
    {"q": "Um triângulo tem quantos lados?", "options": ["3", "4", "5", "6"], "answer": 0, "bloom": 1, "category": "geometria"},
    {"q": "Qual é a soma dos ângulos internos de um triângulo?", "options": ["180°", "360°", "90°", "270°"], "answer": 0, "bloom": 1, "category": "geometria"},
    {"q": "Quanto é 3/5 de 20?", "options": ["12", "15", "10", "8"], "answer": 0, "bloom": 3, "category": "frações"},
    {"q": "Qual é o dobro de 3/8?", "options": ["3/4", "6/16", "3/16", "6/8"], "answer": 0, "bloom": 3, "category": "frações"},
    {"q": "Em uma sequência: 2, 4, 8, 16 — qual é o próximo?", "options": ["32", "24", "18", "20"], "answer": 0, "bloom": 4, "category": "sequências"},
    {"q": "Quanto é (-3) × (-4)?", "options": ["12", "-12", "7", "-7"], "answer": 0, "bloom": 3, "category": "números inteiros"},
    {"q": "Qual é a média de 4, 6 e 8?", "options": ["6", "7", "5", "8"], "answer": 0, "bloom": 3, "category": "estatística"},
    {"q": "Quantos lados tem um hexágono?", "options": ["6", "5", "7", "8"], "answer": 0, "bloom": 1, "category": "geometria"},
]

_CIENCIAS_QUESTIONS = [
    {"q": "Qual planeta é o maior do Sistema Solar?", "options": ["Júpiter", "Saturno", "Netuno", "Terra"], "answer": 0, "bloom": 1, "category": "astronomia"},
    {"q": "Qual é o processo pelo qual as plantas produzem alimento?", "options": ["Fotossíntese", "Respiração", "Digestão", "Fermentação"], "answer": 0, "bloom": 1, "category": "biologia"},
    {"q": "Quantos planetas há no Sistema Solar?", "options": ["8", "9", "7", "10"], "answer": 0, "bloom": 1, "category": "astronomia"},
    {"q": "Qual é o gás necessário para a respiração humana?", "options": ["Oxigênio", "Nitrogênio", "CO₂", "Hélio"], "answer": 0, "bloom": 1, "category": "biologia"},
    {"q": "Qual é a unidade básica da vida?", "options": ["Célula", "Átomo", "Molécula", "Tecido"], "answer": 0, "bloom": 1, "category": "biologia"},
    {"q": "Qual é o planeta mais próximo do Sol?", "options": ["Mercúrio", "Vênus", "Terra", "Marte"], "answer": 0, "bloom": 1, "category": "astronomia"},
    {"q": "O que é um ecossistema?", "options": ["Conjunto de seres vivos e seu ambiente", "Só os animais de uma região", "Só as plantas de uma região", "O clima de uma área"], "answer": 0, "bloom": 2, "category": "ecologia"},
    {"q": "Qual é a função dos pulmões?", "options": ["Troca de gases (oxigênio e CO₂)", "Bombear sangue", "Digerir alimentos", "Filtrar o sangue"], "answer": 0, "bloom": 1, "category": "biologia"},
    {"q": "O que é a cadeia alimentar?", "options": ["Sequência de quem come quem num ecossistema", "O cardápio de um restaurante", "A lista de alimentos nutritivos", "Os animais em extinção"], "answer": 0, "bloom": 2, "category": "ecologia"},
    {"q": "Qual órgão bombeia o sangue no corpo humano?", "options": ["Coração", "Pulmão", "Fígado", "Rim"], "answer": 0, "bloom": 1, "category": "biologia"},
    {"q": "Qual é o satélite natural da Terra?", "options": ["Lua", "Fobos", "Io", "Tritão"], "answer": 0, "bloom": 1, "category": "astronomia"},
    {"q": "O que os produtores fazem na cadeia alimentar?", "options": ["Produzem matéria orgânica por fotossíntese", "Consomem outros organismos", "Decompõem matéria morta", "Parasitam outros seres"], "answer": 0, "bloom": 2, "category": "ecologia"},
    {"q": "Qual é o símbolo químico da água?", "options": ["H₂O", "CO₂", "NaCl", "O₂"], "answer": 0, "bloom": 1, "category": "química"},
    {"q": "O que é metamorfose em insetos?", "options": ["Transformação em fases: ovo, larva, pupa, adulto", "Mudança de cor", "Crescimento gradual sem transformação", "Reprodução assexuada"], "answer": 0, "bloom": 2, "category": "biologia"},
    {"q": "Qual é a camada da atmosfera mais próxima da superfície?", "options": ["Troposfera", "Estratosfera", "Mesosfera", "Termosfera"], "answer": 0, "bloom": 1, "category": "geociências"},
    {"q": "O que é energia renovável?", "options": ["Energia de fontes que se regeneram naturalmente", "Energia do petróleo", "Energia nuclear", "Energia do carvão"], "answer": 0, "bloom": 2, "category": "energia"},
    {"q": "Qual é a função das raízes nas plantas?", "options": ["Absorver água e nutrientes do solo", "Realizar fotossíntese", "Produzir flores", "Transportar sementes"], "answer": 0, "bloom": 1, "category": "biologia"},
    {"q": "Qual gás as plantas liberam na fotossíntese?", "options": ["Oxigênio", "CO₂", "Nitrogênio", "Vapor d'água"], "answer": 0, "bloom": 1, "category": "biologia"},
    {"q": "O que é biodiversidade?", "options": ["Variedade de espécies em um ecossistema", "O número de árvores em uma floresta", "A quantidade de água em um rio", "A temperatura média de um bioma"], "answer": 0, "bloom": 2, "category": "ecologia"},
    {"q": "Qual é o processo pelo qual a água passa de líquido para gás?", "options": ["Evaporação", "Condensação", "Solidificação", "Fusão"], "answer": 0, "bloom": 1, "category": "física"},
    {"q": "O que é uma estrela?", "options": ["Bola de plasma que produz luz por fusão nuclear", "Planeta que reflete luz solar", "Satélite de um planeta", "Asteroide brilhante"], "answer": 0, "bloom": 2, "category": "astronomia"},
    {"q": "Quantas câmaras tem o coração humano?", "options": ["4", "2", "3", "6"], "answer": 0, "bloom": 1, "category": "biologia"},
    {"q": "O que são fósseis?", "options": ["Restos ou marcas de seres vivos preservados em rochas", "Pedras preciosas", "Minerais raros", "Plantas fosforescentes"], "answer": 0, "bloom": 1, "category": "geociências"},
    {"q": "Qual é a força que mantém os planetas em órbita em torno do Sol?", "options": ["Gravidade", "Magnetismo", "Eletricidade", "Atrito"], "answer": 0, "bloom": 1, "category": "física"},
    {"q": "Qual é a diferença entre clima e tempo?", "options": ["Clima é o padrão de longo prazo; tempo é o estado atual da atmosfera", "Clima é hoje; tempo é o histórico", "São sinônimos", "Clima é local; tempo é global"], "answer": 0, "bloom": 4, "category": "geociências"},
]

_LINGUAGEM_QUESTIONS = [
    {"q": "O que é um substantivo?", "options": ["Palavra que nomeia seres, coisas, lugares", "Palavra que indica ação", "Palavra que modifica o verbo", "Palavra que liga orações"], "answer": 0, "bloom": 1, "category": "gramática"},
    {"q": "Qual é o plural de 'anão'?", "options": ["anões", "anãos", "anões ou anãos", "anõs"], "answer": 2, "bloom": 2, "category": "morfologia"},
    {"q": "O que é um sinônimo?", "options": ["Palavra com significado semelhante", "Palavra de sentido oposto", "Palavra que rima", "Palavra derivada"], "answer": 0, "bloom": 1, "category": "semântica"},
    {"q": "Qual é o antônimo de 'feliz'?", "options": ["triste", "alegre", "contente", "satisfeito"], "answer": 0, "bloom": 1, "category": "semântica"},
    {"q": "O que é um adjetivo?", "options": ["Palavra que caracteriza ou qualifica o substantivo", "Palavra que nomeia ação", "Palavra que substitui o substantivo", "Palavra que une frases"], "answer": 0, "bloom": 1, "category": "gramática"},
    {"q": "Qual tipo de texto tem como objetivo convencer o leitor?", "options": ["Dissertativo-argumentativo", "Narrativo", "Descritivo", "Instrucional"], "answer": 0, "bloom": 2, "category": "tipologia textual"},
    {"q": "O que é metáfora?", "options": ["Comparação implícita entre dois termos", "Exagero para chamar atenção", "Repetição de sons", "Personificação de animais"], "answer": 0, "bloom": 2, "category": "figuras de linguagem"},
    {"q": "Qual é a função do parágrafo no texto?", "options": ["Organizar ideias em blocos temáticos", "Decorar o texto visualmente", "Indicar pontuação", "Separar narradores"], "answer": 0, "bloom": 2, "category": "estrutura textual"},
    {"q": "O que é um verbo?", "options": ["Palavra que indica ação, estado ou fenômeno", "Palavra que nomeia objetos", "Palavra que descreve qualidades", "Palavra que conecta frases"], "answer": 0, "bloom": 1, "category": "gramática"},
    {"q": "O que indica a vírgula em uma lista?", "options": ["Separação de elementos enumerados", "Pausa longa no texto", "Início de explicação", "Contradição entre ideias"], "answer": 0, "bloom": 2, "category": "pontuação"},
    {"q": "Qual é a diferença entre 'mal' e 'mau'?", "options": ["'Mal' é advérbio/substantivo; 'mau' é adjetivo", "São sinônimos", "'Mau' é advérbio; 'mal' é adjetivo", "Não há diferença"], "answer": 0, "bloom": 4, "category": "ortografia"},
    {"q": "O que é coerência textual?", "options": ["Unidade de sentido do texto", "Uso correto da gramática", "Variedade de vocabulário", "Presença de figuras de linguagem"], "answer": 0, "bloom": 2, "category": "coesão e coerência"},
    {"q": "O que é um pronome?", "options": ["Palavra que substitui ou acompanha o substantivo", "Verbo no passado", "Tipo de advérbio", "Conjunção subordinativa"], "answer": 0, "bloom": 1, "category": "gramática"},
    {"q": "Qual recurso expressa exagero para criar efeito?", "options": ["Hipérbole", "Eufemismo", "Antítese", "Ironia"], "answer": 0, "bloom": 1, "category": "figuras de linguagem"},
    {"q": "O que é um texto narrativo?", "options": ["Texto que conta uma história com personagens e eventos", "Texto que descreve características", "Texto que defende uma opinião", "Texto que dá instruções"], "answer": 0, "bloom": 2, "category": "tipologia textual"},
    {"q": "O que é intertextualidade?", "options": ["Relação entre dois ou mais textos", "Uso de palavras difíceis", "Citação de dicionário", "Repetição de ideias"], "answer": 0, "bloom": 4, "category": "leitura"},
    {"q": "Qual é a função da conjunção 'mas'?", "options": ["Indica oposição ou contraste", "Indica causa", "Indica consequência", "Indica explicação"], "answer": 0, "bloom": 2, "category": "gramática"},
    {"q": "O que é denotação?", "options": ["Sentido literal da palavra", "Sentido figurado", "Uso irônico", "Duplo sentido"], "answer": 0, "bloom": 1, "category": "semântica"},
    {"q": "O que é conotação?", "options": ["Sentido figurado ou subjetivo da palavra", "Sentido literal", "Sinônimo técnico", "Tradução direta"], "answer": 0, "bloom": 1, "category": "semântica"},
    {"q": "Qual é a estrutura básica de uma narrativa?", "options": ["Introdução, desenvolvimento, clímax, desfecho", "Tese, argumentos, conclusão", "Tema, rima, métrica, estrofe", "Título, subtítulo, corpo"], "answer": 0, "bloom": 1, "category": "estrutura textual"},
    {"q": "O que é crônica?", "options": ["Texto curto sobre cotidiano, geralmente bem-humorado", "Poema épico longo", "Relatório científico", "Carta formal"], "answer": 0, "bloom": 2, "category": "gêneros textuais"},
    {"q": "Qual é o sujeito da frase: 'Os alunos estudaram muito'?", "options": ["Os alunos", "estudaram", "muito", "Os alunos estudaram"], "answer": 0, "bloom": 3, "category": "análise sintática"},
    {"q": "O que é aliteração?", "options": ["Repetição de sons consonantais", "Repetição de vogais", "Rima no final dos versos", "Inversão da ordem das palavras"], "answer": 0, "bloom": 1, "category": "figuras de linguagem"},
    {"q": "O que diferencia fábula de conto?", "options": ["Fábula tem animais com lição moral; conto tem personagens variados", "Fábula é mais longa", "Conto é exclusivamente para crianças", "São sinônimos"], "answer": 0, "bloom": 4, "category": "gêneros textuais"},
    {"q": "Para que serve o discurso direto?", "options": ["Reproduzir a fala de um personagem entre aspas ou travessão", "Descrever cenários", "Conectar parágrafos", "Indicar tempo cronológico"], "answer": 0, "bloom": 2, "category": "estrutura textual"},
]

_HISTORIA_QUESTIONS = [
    {"q": "Em que ano o Brasil proclamou a Independência?", "options": ["1822", "1889", "1808", "1500"], "answer": 0, "bloom": 1, "category": "brasil"},
    {"q": "Quem proclamou a República do Brasil?", "options": ["Marechal Deodoro da Fonseca", "Dom Pedro II", "Tiradentes", "Dom João VI"], "answer": 0, "bloom": 1, "category": "brasil"},
    {"q": "Quando ocorreu a Primeira Guerra Mundial?", "options": ["1914-1918", "1939-1945", "1900-1905", "1918-1922"], "answer": 0, "bloom": 1, "category": "guerra"},
    {"q": "O que foi a Revolução Industrial?", "options": ["Transformação da produção artesanal para fabril com uso de máquinas", "Revolução política na França", "Guerra entre países industrializados", "Movimento operário do século XX"], "answer": 0, "bloom": 2, "category": "história moderna"},
    {"q": "Em que continente surgiu a escrita cuneiforme?", "options": ["Ásia (Mesopotâmia)", "Europa", "África", "América"], "answer": 0, "bloom": 1, "category": "história antiga"},
    {"q": "O que foi a Revolução Francesa?", "options": ["Movimento que derrubou a monarquia e instaurou princípios de liberdade e igualdade", "Guerra civil inglesa", "Independência dos EUA", "Unificação da Itália"], "answer": 0, "bloom": 2, "category": "história moderna"},
    {"q": "Qual civilização construiu as pirâmides de Gizé?", "options": ["Egípcios", "Sumérios", "Gregos", "Romanos"], "answer": 0, "bloom": 1, "category": "história antiga"},
    {"q": "Em que ano ocorreu a abolição da escravatura no Brasil?", "options": ["1888", "1822", "1889", "1850"], "answer": 0, "bloom": 1, "category": "brasil"},
    {"q": "O que foi o Iluminismo?", "options": ["Movimento intelectual que valorizou razão, ciência e liberdade individual", "Reforma religiosa do século XVI", "Conquista do espaço", "Expansão do Império Romano"], "answer": 0, "bloom": 2, "category": "história moderna"},
    {"q": "Qual foi o principal documento da Independência dos EUA?", "options": ["Declaração de Independência (1776)", "Constituição de 1787", "Magna Carta", "Declaração dos Direitos do Homem"], "answer": 0, "bloom": 1, "category": "história moderna"},
    {"q": "O que foi a Inquisição?", "options": ["Tribunal da Igreja Católica para julgar heresias", "Parlamento medieval europeu", "Movimento de reforma protestante", "Cruzada contra os muçulmanos"], "answer": 0, "bloom": 2, "category": "história medieval"},
    {"q": "Quem foi Napoleão Bonaparte?", "options": ["General e imperador francês que dominou grande parte da Europa", "Rei da Prússia", "Líder da Revolução Industrial inglesa", "Explorador português"], "answer": 0, "bloom": 2, "category": "história moderna"},
    {"q": "Quando ocorreu a Segunda Guerra Mundial?", "options": ["1939-1945", "1914-1918", "1929-1935", "1950-1953"], "answer": 0, "bloom": 1, "category": "guerra"},
    {"q": "O que foi o apartheid?", "options": ["Sistema de segregação racial na África do Sul", "Guerra civil americana", "Genocídio na Europa", "Ditadura na América Latina"], "answer": 0, "bloom": 2, "category": "história contemporânea"},
    {"q": "Qual foi o tratado que encerrou a Primeira Guerra Mundial?", "options": ["Tratado de Versalhes", "Paz de Westfália", "Tratado de Utrecht", "Paz de Viena"], "answer": 0, "bloom": 1, "category": "guerra"},
    {"q": "O que foi a Reforma Protestante?", "options": ["Movimento de ruptura com a Igreja Católica no século XVI", "Reforma da educação medieval", "Retorno às práticas do Islã", "Cruzada contra os pagãos"], "answer": 0, "bloom": 2, "category": "história moderna"},
    {"q": "Em que século ocorreu a chegada dos portugueses ao Brasil?", "options": ["XVI (1500)", "XV (1492)", "XVII (1600)", "XVIII (1700)"], "answer": 0, "bloom": 1, "category": "brasil"},
    {"q": "O que foi a Guerra Fria?", "options": ["Tensão política entre EUA e URSS após 1945 sem conflito armado direto", "Guerra na Coreia", "Conflito na América Latina nos anos 1960", "Disputa econômica entre Japão e Europa"], "answer": 0, "bloom": 2, "category": "história contemporânea"},
    {"q": "Quem foi Martin Luther King Jr.?", "options": ["Líder dos direitos civis dos negros nos EUA", "Presidente americano nos anos 1960", "Revolucionário cubano", "Filósofo alemão"], "answer": 0, "bloom": 1, "category": "história contemporânea"},
    {"q": "O que foi o Renascimento?", "options": ["Movimento cultural e artístico que valorizou a antiguidade clássica", "Período das grandes guerras medievais", "Reforma religiosa europeia", "Expansão do império islâmico"], "answer": 0, "bloom": 2, "category": "história moderna"},
    {"q": "Em que país surgiu a Revolução Industrial?", "options": ["Inglaterra", "França", "Alemanha", "Estados Unidos"], "answer": 0, "bloom": 1, "category": "história moderna"},
    {"q": "O que foi o feudalismo?", "options": ["Sistema político e econômico medieval baseado em suserania e vassalagem", "Sistema democrático grego", "Regime colonial ibérico", "Organização tribal africana"], "answer": 0, "bloom": 2, "category": "história medieval"},
    {"q": "Quando o homem pisou na Lua pela primeira vez?", "options": ["1969", "1957", "1961", "1972"], "answer": 0, "bloom": 1, "category": "história contemporânea"},
    {"q": "O que foi a Inconfidência Mineira?", "options": ["Movimento colonial brasileiro contra o domínio português no século XVIII", "Revolta dos escravos em Palmares", "Independência da Bahia", "Proclamação da República"], "answer": 0, "bloom": 2, "category": "brasil"},
    {"q": "Quem foi Dom Pedro I?", "options": ["Primeiro imperador do Brasil, filho de Dom João VI", "Presidente da República", "Governador geral português", "Líder da Inconfidência"], "answer": 0, "bloom": 1, "category": "brasil"},
]

_GENERICO_QUESTIONS = [
    {"q": "Qual é a capital do Brasil?", "options": ["Brasília", "São Paulo", "Rio de Janeiro", "Salvador"], "answer": 0, "bloom": 1, "category": "geografia"},
    {"q": "Quantos estados tem o Brasil?", "options": ["26 estados e 1 Distrito Federal", "25 estados", "27 estados", "30 estados"], "answer": 0, "bloom": 1, "category": "geografia"},
    {"q": "Qual é o maior planeta do Sistema Solar?", "options": ["Júpiter", "Terra", "Saturno", "Urano"], "answer": 0, "bloom": 1, "category": "ciências"},
    {"q": "Quem escreveu 'Dom Quixote'?", "options": ["Miguel de Cervantes", "Luís de Camões", "William Shakespeare", "Dante Alighieri"], "answer": 0, "bloom": 1, "category": "literatura"},
    {"q": "Qual é o resultado de 7 × 8?", "options": ["56", "54", "64", "48"], "answer": 0, "bloom": 3, "category": "matemática"},
    {"q": "Qual é o continente mais populoso?", "options": ["Ásia", "África", "Europa", "Américas"], "answer": 0, "bloom": 1, "category": "geografia"},
    {"q": "Qual é o elemento químico de símbolo 'O'?", "options": ["Oxigênio", "Ouro", "Osmio", "Ósmio"], "answer": 0, "bloom": 1, "category": "química"},
    {"q": "Quem pintou a Mona Lisa?", "options": ["Leonardo da Vinci", "Michelangelo", "Rafael", "Botticelli"], "answer": 0, "bloom": 1, "category": "arte"},
    {"q": "Em que país fica a Torre Eiffel?", "options": ["França", "Itália", "Espanha", "Bélgica"], "answer": 0, "bloom": 1, "category": "geografia"},
    {"q": "Qual é a velocidade da luz?", "options": ["300.000 km/s", "30.000 km/s", "3.000.000 km/s", "150.000 km/s"], "answer": 0, "bloom": 1, "category": "física"},
    {"q": "O que significa 'ONU'?", "options": ["Organização das Nações Unidas", "Organização Nacional Unida", "União das Nações Organizadas", "Nações Unidas do Ocidente"], "answer": 0, "bloom": 1, "category": "política"},
    {"q": "Qual é o idioma mais falado no mundo?", "options": ["Mandarim", "Inglês", "Espanhol", "Hindi"], "answer": 0, "bloom": 1, "category": "cultura"},
    {"q": "Quantos continentes existem?", "options": ["7", "6", "5", "8"], "answer": 0, "bloom": 1, "category": "geografia"},
    {"q": "Qual é o maior oceano do mundo?", "options": ["Pacífico", "Atlântico", "Índico", "Ártico"], "answer": 0, "bloom": 1, "category": "geografia"},
    {"q": "O que é democracia?", "options": ["Sistema de governo onde o poder emana do povo", "Governo de um só líder", "Governo dos mais ricos", "Governo militar"], "answer": 0, "bloom": 2, "category": "política"},
    {"q": "Qual é o rio mais longo do mundo?", "options": ["Nilo", "Amazonas", "Yangtzé", "Mississippi"], "answer": 0, "bloom": 1, "category": "geografia"},
    {"q": "Quem foi Albert Einstein?", "options": ["Físico alemão-americano, criador da teoria da relatividade", "Químico inglês", "Astrônomo italiano", "Matemático francês"], "answer": 0, "bloom": 1, "category": "ciências"},
    {"q": "Qual é o metal mais abundante na crosta terrestre?", "options": ["Alumínio", "Ferro", "Cobre", "Ouro"], "answer": 0, "bloom": 1, "category": "química"},
    {"q": "O que é globalização?", "options": ["Integração econômica, cultural e política entre países", "Fenômeno climático global", "Expansão dos impérios coloniais", "Movimento ambientalista internacional"], "answer": 0, "bloom": 2, "category": "atualidades"},
    {"q": "Qual é a moeda do Brasil?", "options": ["Real", "Peso", "Cruzeiro", "Dólar"], "answer": 0, "bloom": 1, "category": "economia"},
    {"q": "Quantas horas tem um dia?", "options": ["24", "12", "48", "36"], "answer": 0, "bloom": 1, "category": "geral"},
    {"q": "Qual é o animal terrestre mais rápido?", "options": ["Guepardo", "Leão", "Cavalo", "Avestruz"], "answer": 0, "bloom": 1, "category": "biologia"},
    {"q": "Qual é o menor país do mundo?", "options": ["Vaticano", "Mônaco", "San Marino", "Liechtenstein"], "answer": 0, "bloom": 1, "category": "geografia"},
    {"q": "O que é inflação?", "options": ["Aumento generalizado dos preços", "Queda dos juros bancários", "Redução da dívida pública", "Crescimento do PIB"], "answer": 0, "bloom": 2, "category": "economia"},
    {"q": "Qual é o instrumento usado para medir a temperatura?", "options": ["Termômetro", "Barômetro", "Higrômetro", "Anemômetro"], "answer": 0, "bloom": 1, "category": "ciências"},
]

DOMAIN_BANKS: Dict[str, List[Dict]] = {
    "matematica": _MATEMATICA_QUESTIONS,
    "matemática": _MATEMATICA_QUESTIONS,
    "frações": _MATEMATICA_QUESTIONS,
    "fracoes": _MATEMATICA_QUESTIONS,
    "ciencias": _CIENCIAS_QUESTIONS,
    "ciências": _CIENCIAS_QUESTIONS,
    "linguagem": _LINGUAGEM_QUESTIONS,
    "língua portuguesa": _LINGUAGEM_QUESTIONS,
    "lingua portuguesa": _LINGUAGEM_QUESTIONS,
    "português": _LINGUAGEM_QUESTIONS,
    "historia": _HISTORIA_QUESTIONS,
    "história": _HISTORIA_QUESTIONS,
    "generico": _GENERICO_QUESTIONS,
    "geral": _GENERICO_QUESTIONS,
}


def _get_question_bank(domain: Optional[str], topic: Optional[str]) -> List[Dict]:
    """Pick a question bank based on domain/topic."""
    for candidate in (domain, topic):
        if not candidate:
            continue
        key = str(candidate).strip().lower()
        if key in DOMAIN_BANKS:
            return DOMAIN_BANKS[key]
        for bk, questions in DOMAIN_BANKS.items():
            if bk in key or key in bk:
                return questions
    return _GENERICO_QUESTIONS


def _build_track_spaces(n: int) -> List[Dict]:
    """Build space configurations for a track game."""
    rng = random.Random(42)  # deterministic layout for reproducibility
    types = ['normal', 'quiz', 'bonus', 'penalty', 'special']
    weights = [0.5, 0.25, 0.1, 0.1, 0.05]
    icons = {'normal': '', 'quiz': '❓', 'bonus': '⭐', 'penalty': '💀', 'special': '🎁', 'start': '🏁', 'end': '🏆'}
    spaces = []
    for i in range(n):
        if i == 0:
            spaces.append({'type': 'start', 'icon': '🏁'})
        elif i == n - 1:
            spaces.append({'type': 'end', 'icon': '🏆'})
        else:
            r = rng.random()
            cum = 0.0
            t = 'normal'
            for j, tp in enumerate(types):
                cum += weights[j]
                if r < cum:
                    t = tp
                    break
            spaces.append({'type': t, 'icon': icons.get(t, '')})
    return spaces


def build_board_content(
    spec_dict: dict,
    domain: Optional[str] = None,
    topic: Optional[str] = None,
) -> dict:
    """Build the JSON content pack for the board game engine.

    Parameters
    ----------
    spec_dict:
        Parsed spec dict (from DSL or manually constructed).
    domain:
        Educational domain (e.g. 'matematica', 'ciencias').
    topic:
        Specific topic within the domain.

    Returns
    -------
    dict
        Content pack ready to be injected as JSON into the HTML.
    """
    meta = spec_dict.get('metadata', {})
    board = spec_dict.get('board', {})
    rules = spec_dict.get('rules', {})
    config_block = spec_dict.get('config', {})

    # Resolve domain/topic
    dom = domain or meta.get('domain') or meta.get('Domain')
    top = topic or meta.get('topic') or meta.get('Topic')

    question_bank = _get_question_bank(dom, top)
    questions = [dict(q) for q in question_bank]
    random.shuffle(questions)

    board_type = board.get('type', 'track')
    _spaces_raw = board.get('spaces', 36)
    spaces_count = len(_spaces_raw) if isinstance(_spaces_raw, list) else int(_spaces_raw)
    num_players = 2

    players_raw = rules.get('players', meta.get('players', '2..4'))
    if isinstance(players_raw, str) and '..' in str(players_raw):
        num_players = int(str(players_raw).split('..')[0])
    elif isinstance(players_raw, int):
        num_players = players_raw

    title = spec_dict.get('title', 'Board Game Educativo')

    config = {
        'spaces': spaces_count,
        'hand_size': 5,
        'win_score': 15,
        'time_limit': 20,
        'rounds': 15,
        'grid_size': 3,
        'grid_mode': 'ttt',
    }
    config.update(config_block)

    content = {
        'title': title,
        'players': num_players,
        'board_type': board_type,
        'questions': questions,
        'spaces_count': spaces_count,
        'config': config,
        'metadata': {
            'domain': dom,
            'topic': top,
            'bloom': meta.get('bloom'),
            'age_range': meta.get('age_range'),
            'duration': meta.get('duration'),
        },
    }

    # Add space configs for track games
    if board_type in ('track', 'trilha'):
        content['spaces'] = _build_track_spaces(spaces_count)

    return content
