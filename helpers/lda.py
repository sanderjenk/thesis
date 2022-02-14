import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import nltk
nltk.download('wordnet')
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

def get_preprocessed_docs(df):
	
	return df['text'].map(str).map(preprocess_words)

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

	intial_vector = backlog.apply(lambda x: get_topic_vector(x["text"], lda_model, dictionary), axis=1)

	backlog["vector"] = intial_vector.apply(topic_to_vector, args=(number_of_topics,))

	return backlog

def get_lda_model(done_issues_df, number_of_topics):

	preprocessed_docs = get_preprocessed_docs(done_issues_df)

	dictionary = gensim.corpora.Dictionary(preprocessed_docs) 

	dictionary.filter_extremes(no_below=15, no_above=0.7, keep_n=100000)

	bow_corpus = [dictionary.doc2bow(doc) for doc in preprocessed_docs]

	lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=number_of_topics, id2word=dictionary, passes=2, workers=2)

	return lda_model, dictionary

def add_experience_topic_vector_to_users(done_issues_df, lda_model, dictionary, number_of_topics):

	grouping = done_issues_df.groupby("assignee.name")

	user_df = grouping.agg({'text': 'sum'})

	user_df["issue_count"] = grouping["text"].count()

	initial_vector = user_df["text"].apply(get_topic_vector, args=(lda_model,dictionary,))

	user_df["vector"] = initial_vector.apply(topic_to_vector, args=(number_of_topics,))

	return user_df


