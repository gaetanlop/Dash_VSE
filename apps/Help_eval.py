import html
import re
from nltk import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
import dash_html_components as html
import pandas as pd
import numpy as np
import base64
import io
from dash import Dash, dash_table
import dash_html_components as html
from sklearn.neighbors import NearestCentroid
from pandas import DataFrame
from sklearn.cluster import KMeans
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pl
from sklearn.cluster import KMeans
from nltk.cluster import KMeansClusterer, cosine_distance
from wordcloud import WordCloud
from scipy.stats import stats
from sklearn.preprocessing import MinMaxScaler
import nltk
nltk.download('wordnet')


class TrollTfidfVectorizer(TfidfVectorizer):

    def __init__(self, *args, **kwargs):
        troll_stop_words = {'don', 'just', 'like'} # the custom stop word list could be further expanded
        kwargs['stop_words'] = set(ENGLISH_STOP_WORDS).union(troll_stop_words)
        kwargs['preprocessor'] = self.vectorizer_preprocess
        self.wnl = WordNetLemmatizer()
        super(TrollTfidfVectorizer, self).__init__(*args, **kwargs)

    def build_analyzer(self):
        analyzer = super(TfidfVectorizer, self).build_analyzer()
        return lambda doc: ([self.wnl.lemmatize(w) for w in analyzer(doc)])

    def vectorizer_preprocess(self, s):
        # remove urls
        s = re.sub(r'(https?|ftp)://(-\.)?([^\s/?\.#-]+\.?)+(/[^\s]*)?', '', s)
        # remove amp
        s = s.replace('&amp;', '')
        # remove RT signs (no meaning) but keep username
        s = re.sub(r'\bRT\b\s+', '', s)
        s = s.lower()
        return s


def get_dataframe(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                temp = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8', errors='ignore')), sep=";")
            elif 'xls' in filename:
                # Assume that the user uploaded an excel file
                temp = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])

        return temp.to_dict()
    else:
        return [()]


def fact_checking_assignment(dataset, n_clusters):
    vectorizer = TrollTfidfVectorizer(max_features=100, min_df=0.01)
    column = dataset.columns[0]
    doc_term_matrix = vectorizer.fit_transform(dataset[column].values)

    model = KMeans(n_clusters=n_clusters, init='k-means++', n_init=1)
    cluster_labels = model.fit_predict(doc_term_matrix)

    dff = dataset.copy()

    dff["cluster_labels"] = cluster_labels
    print(dff.head(10))
    return dff.to_dict()


def dfFromModel(model, vectorizer, data, cluster_labels, transformation=None):
    if hasattr(model, 'cluster_centers_'):
        cluster_centers = model.cluster_centers_
    else:
        # https://stackoverflow.com/questions/56456572/how-to-get-agglomerative-clustering-centroid-in-python-scikit-learn

        clf = NearestCentroid()
        clf.fit(data, cluster_labels)
        cluster_centers = clf.centroids_
    if transformation == None:
        transformed = cluster_centers
    elif transformation == "zscore" or transformation == "zscore_rescaled":
        zscore = stats.zscore(cluster_centers, axis=0)
        if transformation == "zscore_rescaled":
            # data are flattened into one long vector
            zscore_flattened = zscore.reshape(zscore.shape[0] * zscore.shape[1], 1)
            # rescaled
            # MinMaxScaler preserves the shape of the original distribution.
            scaler = MinMaxScaler((0, 100))
            # find maximum absolute z score
            bound = max(max(zscore_flattened), abs(min(zscore_flattened)))
            # use the maximum z score to create transformation centered around 0
            scaler.fit(np.array([-bound, bound]))
            # scaler.fit(zscore_flattened) # originaly the transformation was fitted without the centering
            # owing to the centering, after the transformation, value 50 corresponds to zscore 0
            zscore_flattened_scaled = scaler.transform(zscore_flattened)
            # and transformed back to the original shape
            zscore_scaled = zscore_flattened_scaled.reshape(zscore.shape[0], zscore.shape[1])
            transformed = zscore_scaled
        else:
            transformed = zscore
    dataframe = DataFrame(transformed, columns=vectorizer.get_feature_names())
    return (dataframe)


def fig_to_uri(in_fig, close_all=True, **save_args):
    """
    Save a figure as a URI
    :param in_fig:
    :return:
    """
    out_img = io.BytesIO()
    in_fig.savefig(out_img, format='png', **save_args)
    if close_all:
        in_fig.clf()
        pl.close('all')
    out_img.seek(0)
    encoded = base64.b64encode(out_img.read()).decode("ascii").replace("\n", "")
    return "data:image/png;base64,{}".format(encoded)


def get_dataframe_wordcloud(df):
    print("vectorizing")
    column = "Tweets"
    distance = "cosine"
    init = "random"
    n_clusters = 3
    MAX_WORDS_WORDCLOUD = 100
    vectorizer = TrollTfidfVectorizer(max_features=100, min_df=0.01)
    doc_term_matrix = vectorizer.fit_transform(df[column].values)
    print("vectorizing done")

    data = doc_term_matrix.toarray()

    model = KMeans(n_clusters=n_clusters, init='k-means++', n_init=1)
    cluster_labels = model.fit_predict(doc_term_matrix)

    my_cluster = cluster_labels[-1]
    data=data[:-1]
    cluster_labels=cluster_labels[:-1]

    wordclouds = wordcloud(dfFromModel(model, vectorizer, data, cluster_labels,"zscore_rescaled"), spectral=True, max_words=MAX_WORDS_WORDCLOUD)

    return fig_to_uri(wordclouds), my_cluster


def wordcloud(dataframe, spectral=False, max_words=200, vertical=1, horizontal=3):
    clusters_word_freq = []

    for index, row in dataframe.iterrows():
        freq_dict = {}
        for col_name in dataframe.columns:
            if row[col_name] > 0.00001:
                freq_dict[col_name] = float(row[col_name])
        clusters_word_freq.append(freq_dict)

    fig = pl.figure(figsize=(60, 20))
    for cluster, freq_dict in enumerate(clusters_word_freq):
        if spectral:  # used for wordclouds from zscores, coolwarm goes from blue to red
            def color_func(word, *args, **kwargs):
                cmap = pl.cm.get_cmap('coolwarm')
                # Colormap instances are used to convert data values (floats) from the interval [0, 1] to the RGBA color
                rgb = cmap(freq_dict[word] / 100, bytes=True)[0:3]
                return rgb
        else:
            color_func = None

        ax = fig.add_subplot(vertical, horizontal, cluster + 1)
        cloud = WordCloud(normalize_plurals=False,
                          background_color='white', color_func=color_func, max_words=max_words, random_state=42)
        # classwordcloud.WordCloud(font_path=None, width=400, height=200, margin=2, ranks_only=None, prefer_horizontal=0.9, mask=None, scale=1, color_func=None, max_words=200, min_font_size=4, stopwords=None, random_state=None, background_color='black', max_font_size=None, font_step=1, mode='RGB', relative_scaling='auto', regexp=None, collocations=True, colormap=None, normalize_plurals=True, contour_width=0, contour_color='black', repeat=False, include_numbers=False, min_word_length=0, collocation_threshold=30)
        cloud.generate_from_frequencies(frequencies=freq_dict)
        ax.imshow(cloud, interpolation='bilinear')
        ax.set_yticks([])
        ax.set_xticks([])
        ax.text(0.35, 1, f'Cluster {cluster}',
                fontsize=32, va='bottom', transform=ax.transAxes)

    return fig


def plot_wordcloud(temp):
    wordclouds, my_cluster = get_dataframe_wordcloud(temp)

    return html.Div([
        html.P("Please find below visualizations of the different clusters")
    ]), wordclouds, my_cluster