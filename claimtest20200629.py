import numpy as np
from scipy import spatial
import gensim

#load word2vec model, here GoogleNews is used
model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
#two sample sentences 
#model = gensim.models.KeyedVectors.load_word2vec_format(model_file, binary=True)
index2word_set = set(model.wv.index2word)


def avg_feature_vector(sentence, model, num_features, index2word_set):
    words = sentence.split()
    feature_vec = np.zeros((num_features, ), dtype='float32')
    n_words = 0
    for word in words:
        if word in index2word_set:
            n_words += 1
            feature_vec = np.add(feature_vec, model[word])
    if (n_words > 0):
        feature_vec = np.divide(feature_vec, n_words)
    return feature_vec


#比較 US9459234B2 的 Claim 1 及 Claim 12 相似度
sentance1="A BioFET device, comprising: a substrate having an active region comprising a semiconductor material; a gate structure disposed on a first surface of the semiconductor material of the substrate; a source region and a drain region in the semiconductor material, wherein a channel region interposes the source and drain region; an isolation layer disposed over a second surface of the semiconductor material of the substrate, the second surface opposing the first surface, wherein the isolation layer includes an opening over a first portion of the second surface in the channel region and wherein the isolation layer covers a second portion of the second surface in the channel region and the isolation layer covers the second surface in each of the source region and drain region; and an interface layer formed on the second surface of the substrate in the opening, wherein the interface layer includes a metal layer that is directly on the second surface of the semiconductor material of the channel region, wherein a top surface of the interface layer is below a top surface of the isolation layer."
sentance2="A BioFET device, comprising: a FET device on a semiconductor substrate, wherein the FET device includes a gate structure formed on a first surface of the semiconductor substrate and a channel region within the semiconductor substrate wherein the channel region interposes a source region and a drain region in the semiconductor substrate; an opening in an isolation layer disposed on a second surface of the semiconductor substrate, the second surface being parallel to and opposing the first surface, wherein the opening exposes the channel region of the FET device, the channel region including a portion of the second surface of the semiconductor substrate; an interface material on the channel region of the second surface of the semiconductor substrate in the opening; a multi-layer interconnect (MLI) on the first surface of the semiconductor substrate, wherein the MLI includes a first metal layer and a second metal layer interposed by an inter-layer dielectric (ILD) layer and connected by a conductive via, wherein the first and second metal layer are disposed a greater distance from the first surface of the semiconductor material than the gate structure; a trench extending from the second surface of the semiconductor substrate through the semiconductor substrate to the first metal layer of the MLI, wherein the trench is disposed a distance from each of the channel, source and drain regions; and an interconnect layer disposed in the trench and on the first metal layer, and wherein the interconnect layer forms an input/output (I/O) region over the isolation layer on the second surface of the semiconductor substrate, wherein the I/O region is spaced a lateral distance from the opening in the isolation layer, the source region and the drain region."

s1_afv = avg_feature_vector(sentance1, model=model, num_features=300, index2word_set=index2word_set)
s2_afv = avg_feature_vector(sentance2, model=model, num_features=300, index2word_set=index2word_set)
sim = 1 - spatial.distance.cosine(s1_afv, s2_afv)


print(sim)
