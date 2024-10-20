import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import sys
import enchant

from sentence_transformers import SentenceTransformer, util
from statistics import mean
import torch


# Funcao para obter representacoes de vetores do modelo para um texto
def get_embedding(text, tokenizer, model):
    with torch.no_grad():
        inputs = tokenizer(text, return_tensors="pt")
        outputs = model(**inputs)
        return outputs.last_hidden_state[:, 0, :].numpy()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Quantidade incorreta de argumentos providos.")
        sys.exit(1)

    software_testing_content_path = sys.argv[1] # caminho do txt com o conteudo dos artigos
    df_ans_path = sys.argv[2] # caminho do excel com as respostas do chatbot


    # Conteudo dos artigos da conferencia de software testing
    s_testing_content = open(software_testing_content_path, 'r').read()
    # Dividindo o conteudo em palavras individuais
    s_testing_content = s_testing_content.split()
    # Removendo duplicatas
    s_testing_content = list(set(s_testing_content))

    # Filtrando somente palavras em ingles da lista
    d = enchant.Dict("en_US")
    s_testing_content_words = []
    for word in s_testing_content:
        if d.check(word):
            s_testing_content_words.append(word)

    # Carregando o modelo e o tokenizador
    model_name = "sentence-transformers/paraphrase-MiniLM-L6-v2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # Dominio de conhecimento
    domain = "software testing"
    domain_embedding = get_embedding(domain)
    # Gerando representacoes para cada palavra dos artigos
    word_embeddings = np.array([get_embedding(word) for word in s_testing_content_words])

    # Calculando o BERTScore via similaridade do cosseno
    similarities = []
    for w in word_embeddings:
        c_s = cosine_similarity(domain_embedding, w)
        similarities.append(c_s.item())


    # Filtrando as 100 palavras com maior BERTScore quando comparadas com "software testing"
    top_n = 100
    sorted_positions = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)
    largest_positions = sorted_positions[:top_n]
    topics = [s_testing_content_words[i] for i in largest_positions]

    # Lendo a tabela com as perguntas e respostas do chatbot
    df_ans = pd.read_excel(df_ans_path)
    questions = df_ans.question.unique().tolist()


    # Obtendo a representacao vetorial dos topicos
    topic_emb = model.encode(topics, convert_to_tensor=True)

    # Calculate the average embedding for all topics
    avg_topic_emb = torch.mean(topic_emb, dim=0)

    question_score = list()
    no_con_score = list()
    con_score = list()

    for i in range(df_ans.shape[0]):
        # Calculating the embeddings
        q_emb = model.encode(df_ans.iloc[i].question, convert_to_tensor=True)
        no_con_emb = model.encode(df_ans.iloc[i].no_context_answer, convert_to_tensor=True)
        con_emb = model.encode(df_ans.iloc[i].context_answer, convert_to_tensor=True)

        question_score.append(util.pytorch_cos_sim(q_emb, avg_topic_emb).item())
        no_con_score.append(util.pytorch_cos_sim(no_con_emb, avg_topic_emb).item())
        con_score.append(util.pytorch_cos_sim(con_emb, avg_topic_emb).item())


    # Criando o dataframe com os scores
    df_ans.loc[:,'score_question']   = question_score
    df_ans.loc[:,'score_ans_no_con'] = no_con_score
    df_ans.loc[:,'score_ans_con']    = con_score


    # Salvando o novo dataframe
    df_ans.to_excel('df_bert_score.xlsx')

