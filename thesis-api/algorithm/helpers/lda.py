import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from gensim.models import CoherenceModel
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
# import nltk
# nltk.download('wordnet')
import numpy as np

# past and future tenses to present, third person to first person
def lemmatize_stemming(text):

    return SnowballStemmer("english").stem(WordNetLemmatizer().lemmatize(text, pos='v'))

# remove stopwords and words that have 3 or less characters
def preprocess_words(text):

    result = []

    for token in gensim.utils.simple_preprocess(text):

        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:

            result.append(lemmatize_stemming(token))

    return result

def add_preprocessed_text(df):
    
	df["preprocessed_text"] = df['text'].map(str).map(preprocess_words)
 
	return df

def get_topic_vector(text, lda, dictionary):

    bow_vector = dictionary.doc2bow(preprocess_words(text))

    topic_vector = lda[bow_vector]

    return [x for x in topic_vector]

def topic_to_vector(topic, number_of_topics):

    vector = np.zeros(number_of_topics)

    for x in topic:
        vector[x[0]] = x[1]

    return vector

def add_topic_vector_to_baclog_issues(backlog, lda_model, dictionary, number_of_topics):
    
    if backlog.empty:
        raise Exception("Empty backlog") 
        
    initial_vector = backlog.apply(lambda x: get_topic_vector(x["text"], lda_model, dictionary), axis=1)

    backlog["vector"] = initial_vector.apply(topic_to_vector, args=(number_of_topics,))

    return backlog

def get_lda_model(done_issues_df, number_of_topics, alpha, beta):

    preprocessed_docs = done_issues_df["preprocessed_text"]
    
    dictionary = get_dictionary(preprocessed_docs) 

    dictionary.filter_extremes(no_below=15, no_above=0.7, keep_n=100000)

    bow_corpus = get_bow_corpus(dictionary, preprocessed_docs)

    lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=number_of_topics, id2word=dictionary, passes=2, workers=2, alpha=alpha, eta=beta)

    return lda_model, dictionary

def get_dictionary(preprocessed_docs):
    
    return gensim.corpora.Dictionary(preprocessed_docs) 

def get_bow_corpus(dictionary, preprocessed_docs):
    
    return [dictionary.doc2bow(doc) for doc in preprocessed_docs]

def add_experience_topic_vector_to_users(done_issues_df, lda_model, dictionary, number_of_topics):

    grouping = done_issues_df.groupby("assignee.name")

    user_df = grouping.agg({'text': 'sum'}).reset_index()

    user_df["issue_count"] = grouping["text"].count()

    initial_vector = user_df["text"].apply(get_topic_vector, args=(lda_model,dictionary,))

    user_df["vector"] = initial_vector.apply(topic_to_vector, args=(number_of_topics,))

    return user_df

def get_user_experience_topic_vector(user_done_issues_df, lda_model, dictionary, number_of_topics):
    
    corpus = ' '.join(user_done_issues_df["text"])
    
    topic_vector = get_topic_vector(corpus, lda_model, dictionary)
    
    topic_vector_correct_format = topic_to_vector(topic_vector, number_of_topics)
    
    return topic_vector_correct_format

def get_coherence_value(corpus, dictionary, lemmatized_data, k, a, b):
    
    lda_model = gensim.models.LdaMulticore(corpus=corpus,
                                           id2word=dictionary,
                                           num_topics=k, 
                                           random_state=100,
                                           chunksize=100,
                                           passes=10,
                                           alpha=a,
                                           eta=b)
    
    coherence_model_lda = CoherenceModel(model=lda_model, texts=lemmatized_data, dictionary=dictionary, coherence='c_v')
    
    return coherence_model_lda.get_coherence()

def get_parameter_lists():
    # Topics range
    min_topics = 2
    max_topics = 11
    step_size = 1
    topics_range = range(min_topics, max_topics, step_size)

    # Alpha parameter
    alpha = list(np.arange(0.01, 1, 0.3))
    alpha.append('symmetric')
    alpha.append('asymmetric')

    # Beta parameter
    beta = list(np.arange(0.01, 1, 0.3))
    beta.append('symmetric')
    
    print(len(beta), len(alpha), len(topics_range))
    
    return topics_range, alpha, beta