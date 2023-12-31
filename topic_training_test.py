from mallet_wrapper.coherencemodel import CoherenceModel
from mallet_wrapper.ldamallet import LdaMallet
import mallet_wrapper.corpora as corpora
from datetime import datetime
import mallet_wrapper


def topic_training_mallet_new(dataset, name_dataset, user, topics, mallet_path, chunking=True, optimize_interval_mallet=500, iterations_mallet=5000, random_seed_mallet=100):



    id2word = corpora.Dictionary(dataset)

    corpus = [id2word.doc2bow(text) for text in dataset]

    lda_model_mallet = LdaMallet(mallet_path, corpus=corpus, id2word=id2word,
                                                                  num_topics=topics, iterations=iterations_mallet,
                                                                  optimize_interval=optimize_interval_mallet,
                                                                  random_seed=random_seed_mallet)

    ## Daten-Output Mallet konvertieren

    doc_tops_import = open(lda_model_mallet.fdoctopics(), mode='r', encoding='UTF-8').read()

    doc_tops_mallet = []
    sum_top_weights = 0.0
    top_counter = 0
    min_weight_mallet = 1
    max_weight_mallet = 0
    for line in doc_tops_import.splitlines():
        doc_tops_transfer = []
        for topic_nr, topic in enumerate(line.split()):
            if '.' in topic:
                topic_float = float(topic)
                if topic_float >= 0:  # Threshold für Weight
                    sum_top_weights = sum_top_weights + topic_float
                    top_counter += 1
                    doc_tops_transfer.append((topic_nr - 2,
                                              topic_float))  # hier Weight als Float, in anderen Zellen als Str -> vereinheitlichen (?)
                    if topic_float < min_weight_mallet:
                        min_weight_mallet = topic_float
                    if topic_float > max_weight_mallet:
                        max_weight_mallet = topic_float
        doc_tops_mallet.append(doc_tops_transfer)

    average_weight_mallet = sum_top_weights / top_counter

    topwords_mallet = lda_model_mallet.print_topics(num_topics=topics, num_words=1000)

    coherence_model_ldamallet = CoherenceModel(model=lda_model_mallet,
                                               texts=dataset, dictionary=id2word, coherence='c_v')
    coherence_ldamallet = coherence_model_ldamallet.get_coherence()
    print('\nCoherence Score: ', coherence_ldamallet)

    print('Minimales Topic-Weight Mallet: ' + str(min_weight_mallet))
    print('Durchschnittliches Topic-Weight Mallet: ' + str(average_weight_mallet))
    print('Maximales Topic-Weight Mallet: ' + str(max_weight_mallet))

    now = str(datetime.now())[:19]

    # modeldumps = 'modeldumps/'
    #
    # try:
    #     os.mkdir(modeldumps)
    #     print('Ordner "Modeldumps" wurde erstellt.')
    # except FileExistsError:
    #     print('Ordner "Modeldumps" existiert bereits.')
    #
    # new_model_mallet = 'mallet_' + name_dataset + '_' + str(topics) + 'topics_' + now + '/'
    # os.mkdir(modeldumps + new_model_mallet)
    # doc_tops_mallet_df = pd.DataFrame(data=doc_tops_mallet)
    # doc_tops_mallet_df.to_pickle(
    #     modeldumps + new_model_mallet + user + '_mallet_' + name_dataset + '_' + str(
    #         topics) + 'topics_' + now + '.doc_tops_mallet')
    # top_words_mallet_df = pd.DataFrame(data=lda_model_mallet.print_topics(num_topics=topics, num_words=1000))
    # top_words_mallet_df.to_pickle(
    #     modeldumps + new_model_mallet + user + '_mallet_' + name_dataset + '_' + str(
    #         topics) + 'topics_' + now + '.top_words_mallet')
    # out = open(modeldumps + new_model_mallet + user + '_mallet_' + name_dataset + '_' + str(
    #     topics) + 'topics_' + now + '.txt', 'w', encoding='UTF-8')
    # out.write(name_dataset + '\n')
    # out.write('Anzahl Topics: ' + str(topics) + '\n')
    # out.write('random_seed_mallet: ' + str(random_seed_mallet) + '\n')
    # out.write('optimiize_interval_mallet: ' + str(optimize_interval_mallet) + '\n')
    # out.write('iterations_mallet: ' + str(iterations_mallet) + '\n')
    # out.write('Coherence Score: ' + str(coherence_ldamallet) + '\n')
    # out.write('Minimales Topic-Weight Gensim: ' + str(min_weight_mallet) + '\n')
    # out.write('Durchschnittliches Topic-Weight Gensim: ' + str(average_weight_mallet) + '\n')
    # out.write('Maximales Topic-Weight Gensim: ' + str(max_weight_mallet) + '\n')
    # out.close()

    return lda_model_mallet, doc_tops_mallet, topwords_mallet


#Es brauch keine unterscheidung mehr zwischen gensim und mallet, bei der Ausgabe der Topics.

def print_topics(topic_dictionary, number_of_words, name_dataset, save_doc=False):
    from datetime import datetime
    import re
    import gensim
    import pandas as pd
    import json

    now = str(datetime.now())[:19]
    now_formatted = now[2:4] + now[5:7] + now[8:10] + now[11:13] + now[14:16] + now[17:19]
    now = now_formatted

    if type(topic_dictionary) is not dict:
        top_dic = json.loads(topic_dictionary)
    else:
        top_dic = topic_dictionary

    word_dic = {}

    if save_doc:
                out = open('keywords_mallet_' + name_dataset + '_'+ 'topics_' + str(number_of_words) + 'keywords' + now + '.txt', 'w',
                           encoding='UTF-8')
                for top_words in top_dic["words"]:
                    out_line = []
                    for i in range(number_of_words):
                        out_line.append((top_dic["words"][top_words])[i][1])
                    out.write("Topic " + "\n" + str(top_words) + "\n")
                    out.write(str(out_line) + "\n")
                    out.write("\n")
                    word_dic[top_words] = out_line
                out.close

    else:
                for top_words in top_dic["words"]:
                    out_line = []
                    for i in range(number_of_words):
                        out_line.append((top_dic["words"][top_words])[i][1])
                    word_dic[top_words] = out_line

    pd.set_option('display.max_colwidth', None)

    words_df = pd.DataFrame([', '.join([term for term in word_dic[topic]]) for topic in word_dic], columns = ['Terms per Topic'], index=['Topic'+str(topic) for topic in word_dic])
    words_df.style.set_properties(**{'text-align': 'left'})
    # print(words_df)
