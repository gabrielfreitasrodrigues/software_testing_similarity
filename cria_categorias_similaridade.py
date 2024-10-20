import pandas as pd
import sys


def faixas_score(df, col):
    """
    Funcao que retorna a tabela com uma coluna de categorias dissimilaridade, 
    similaridade baixa, similaridade média e similaridade alta
    
    df: dataframe com a coluna de score
    col: coluna de score a serem criadas faixas
    """
    ####################### Removendo outliers ###################################
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)

    # Calculando o intervalo interquartil (IQR)
    IQR = Q3 - Q1
    k = 1.5
    # Definindo os limites dos outliers
    lower_bound = Q1 - k * IQR
    upper_bound = Q3 + k * IQR

    # Removendo os outliers
    df_no_outliers = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    ##############################################################################

    # Calculando a media e o desvio
    media = df_no_outliers[col].mean()
    desvio = df_no_outliers[col].std()

    media_menos_desvio = media - desvio
    media_mais_desvio = media + desvio
    new_col = 'faixas_' + col

    def conditions(tb):
        if tb[col] < media_menos_desvio:
            return 'dissimilaridade'
        elif (tb[col] >= media_menos_desvio) & (tb[col] < media):
            return 'similaridade baixa'
        elif (tb[col] >= media) & (tb[col] < media_mais_desvio):
            return 'similaridade média'
        elif (tb[col] >= media_mais_desvio):
            return 'similaridade alta'
        else:
            'indefinido'

    # Criando a coluna com as categorias
    df[new_col] = df.apply(conditions, axis=1)

    return df


if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("Quantidade incorreta de argumentos providos.")
        sys.exit(1)

    # Caminho do excel com as perguntas e respostas do chatbot e as colunas de score calculadas
    path_df_score = sys.argv(1)
    df = pd.read_excel(path_df_score)


    # Criando as colunas de categorias
    df = faixas_score(df, 'score_question')
    df = faixas_score(df, 'score_ans_no_con')
    df = faixas_score(df, 'score_ans_con')

    # Salvando a tabela
    df.to_excel('df_categ_similaridade.xlsx')