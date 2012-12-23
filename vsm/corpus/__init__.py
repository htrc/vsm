import numpy as np



#TODO: Documentation update.



def split_corpus(arr, indices):
    """
    """
    if len(indices) == 0:

        return arr

    out = np.split(arr, indices)

    if (indices >= arr.size).any():

        out = out[:-1]

    for i in xrange(len(out)):

        if out[i].size == 0:

            out[i] = np.array([], dtype=arr.dtype)

    return out



class BaseCorpus(object):
    """
    A BaseCorpus object stores a corpus along with its tokenizations
    (e.g., as sentences, paragraphs or documents).

    BaseCorpus aims to provide an efficient method for viewing the
    corpus in tokenized form (i.e., without copying). It currently
    achieves this by storing the corpus as a numpy `ndarray`. Viewing
    a tokenization is carried out using the `view` facilities of numpy
    ndarrays. See documentation on `numpy.ndarray` for further
    details.

    **This documentation is out-of-date.**
    
    Parameters
    ----------
    corpus : array-like
        Array, typically of strings or integers, of atomic terms (or
        tokens) making up the corpus.
    tok_data : list with 1-D array-like elements, optional
        Each element in `tok_data` is an array containing the indices
        marking the token boundaries. An element in `tok_data` is
        intended for use as a value for the `indices_or_sections`
        parameter in `numpy.split`. Elements of `tok_data` may also be
        1-D arrays whose elements are pairs, where the first element
        is a token boundary and the second element is metadata
        associated with that token preceding that boundary. For
        example, (250, 'dogs') might indicate that the 'article' token
        ending at the 250th term of the corpus is named 'dogs'.
        Default is `None`.
    tok_names : array-like, optional
        Each element in `tok_names` is a name of a tokenization in
        `tok_data`.
    dtype : data-type, optional
        The data-type used to interpret the corpus. If omitted, the
        data-type is determined by `numpy.asarray`. Default is `None`.

    Attributes
    ----------
    corpus : 1-D array
        Stores the value of the `corpus` parameter after it has been
        cast to a array of data-type `dtype` (if provided).
    terms : 1-D array
        The indexed set of atomic terms appearing in `corpus`.
        Computed on initialization by `_extract_terms`.
    tok_names: 1-D array-like

    tok_data: list of 1-D array-like

    Methods
    -------
    view_tokens
        Takes a name of tokenization and returns a view of the corpus
        tokenized accordingly.
    view_metadata

    Examples
    --------

    >>> corpus = ['the', 'dog', 'chased', 'the', 'cat',
                  'the', 'cat', 'ran', 'away']
    >>> tok_names = ['sentences']
    >>> tok_data = [[(5, 'transitive'), (9, 'intransitive')]]

    >>> from vsm.corpus import BaseCorpus
    >>> c = BaseCorpus(corpus, tok_names=tok_names, tok_data=tok_data)
    >>> c.corpus
    array(['the', 'dog', 'chased', 'the', 'cat', 'the', 'cat',
           'ran', 'away'], dtype='|S6')
           
    >>> c.terms
    array(['ran', 'away', 'chased', 'dog', 'cat', 'the'],
          dtype='|S6')

    >>> c.view_tokens('sentences')
    [array(['the', 'dog', 'chased', 'the', 'cat'],
          dtype='|S6'),
     array(['the', 'cat', 'ran', 'away'],
          dtype='|S6')]

    >>> c.view_metadata('sentences')[0]
    'transitive'

    """
    def __init__(self,
                 corpus,
                 dtype=None,
                 tok_names=[],
                 tok_data=[]):

        self.corpus = np.asarray(corpus, dtype=dtype)

        self.dtype = self.corpus.dtype

        self._extract_terms()

        self.tok_data = []

        for t in tok_data:

            if self._validate_indices(t['idx']):

                self.tok_data.append(t)

        self._gen_tok_names(tok_names)



    def _gen_tok_names(self, tok_names):

        if self.tok_data:

            a = len(tok_names) if tok_names else 0

            for i in xrange(a, len(self.tok_data)):

                tok_names.append('tok_' + str(i))

        self.tok_names = tok_names



    def _validate_indices(self, indices):
        """
        Checks for invalid tokenizations. Specifically, checks to see
        that the list of indices are sorted and are in range. Ignores
        empty tokens.

        Parameters
        ----------
        indices : 1-D integer array-like

        Returns
        -------
        True if the indices are validated

        Raises
        ------
        Exception

        See Also
        --------
        BaseCorpus
        """
        for i, j in enumerate(indices):
                    
            if i < len(indices) - 1 and j > indices[i + 1]:

                msg = 'malsorted tokenization:'\
                      ' tok ' + str(j) + ' and ' + str(indices[i + 1])

                raise Exception(msg)
                    
            if j > self.corpus.shape[0]:

                msg = 'invalid tokenization'\
                      ' : ' + str(j) + ' is out of range ('\
                      + str(self.corpus.shape[0]) + ')'
                
                raise Exception(msg)

        return True



    def view_metadata(self, name):
        """
        Displays the metadata corresponding to a tokenization of the
        corpus.

        Parameters
        ----------
        name : string-like
            The name of a tokenization.

        Returns
        -------
        The metadata for a tokenization.

        See Also
        --------
        BaseCorpus
        """
        i = self.tok_names.index(name)

        return self.tok_data[i]



    def meta_int(self, tok_name, query):
        """
        """
        tok = self.view_metadata(tok_name)

        ind_set = np.ones(tok.size, dtype=bool)

        for k,v in query.iteritems():

            ind_set = np.logical_and(ind_set, (tok[k] == v))

        n = np.count_nonzero(ind_set)

        if n == 0:

            raise Exception('No token fits that description.')

        elif n > 1:

            msg = ('Multiple tokens fit that description:\n'
                   + str(tok[ind_set]))

            raise Exception(msg)

        return ind_set.nonzero()[0][0]



    def get_metadatum(self, tok_name, query, field):
        """
        """
        i = self.meta_int(tok_name, query)

        datum = self.view_metadata(tok_name)[i][field]

        return datum



    def view_tokens(self, name):
        """
        Displays a tokenization of the corpus.

        Parameters
        ----------
        name : string-like
           The name of a tokenization.

        Returns
        -------
        A tokenized view of `corpus`.

        See Also
        --------
        BaseCorpus
        numpy.split

        """
        i = self.tok_names.index(name)

        indices = self.tok_data[i]['idx']
        
        tokens = split_corpus(self.corpus, indices)

        return tokens


    
    def _extract_terms(self):
        """
        Produces an indexed set of terms from a corpus.
        
        Parameters
        ----------
        corpus : array-like
        
        Returns
        -------
        An indexed set of the elements in `corpus` as a 1-D array.
        
        See Also
        --------
        BaseCorpus
        
        Notes
        -----
        """

        # Benchmarked by Peter Bengtsson
        # (http://www.peterbe.com/plog/uniqifiers-benchmark)
        
        term_set = set()
        
        term_list = [term for term in self.corpus
                     if term not in term_set and not term_set.add(term)]
        
        self.terms = np.array(term_list, dtype=self.corpus.dtype)






class Corpus(BaseCorpus):
    """
    The goal of the Corpus class is to provide an efficient
    representation of a textual corpus.

    A Corpus object contains an integer representation of the text and
    maps to permit conversion between integer and string
    representations of a given term.

    As a BaseCorpus object, it includes a dictionary of tokenizations
    of the corpus and a method for viewing (without copying) these
    tokenizations. This dictionary also stores metadata (e.g.,
    document names) associated with the available tokenizations.

    **This documentation is out-of-date.**

    Parameters
    ----------
    corpus : array-like
        A string array representing the corpus as a sequence of atomic
        terms.
    tok_data : list-like with 1-D integer array-like elements, optional
        Each element in `tok_data` is an array containing the indices
        marking the token boundaries. An element in `tok_data` is
        intended for use as a value for the `indices_or_sections`
        parameter in `numpy.split`. Elements of `tok_data` may also be
        1-D arrays whose elements are pairs, where the first element
        is a token boundary and the second element is metadata
        associated with that token preceding that boundary. For
        example, (250, 'dogs') might indicate that the 'article' token
        ending at the 250th term of the corpus is named 'dogs'.
        Default is `None`.
    tok_names : array-like, optional
        Each element in `tok_names` is a name of a tokenization in
        `tok_data`.

    Attributes
    ----------
    corpus : 1-D 32-bit integer array
        corpus is the integer representation of the input string
        array-like value value of the corpus parameter
    terms : 1-D string array
        The indexed set of strings occurring in corpus. It is a
        string-typed array.
    terms_int : 1-D 32-bit integer array
        A dictionary whose keys are `terms` and whose values are their
        corresponding integers (i.e., indices in `terms`).
    tok : dict with 1-D numpy arrays as values
        The tokenization dictionary. Stems of key names are given by
        `tok_names`. A key name whose value is the array of indices
        for a tokenization has the suffix '_indices'. A key name whose
        value is the metadata array for a tokenization has the suffix
        '_metadata'.
        
    Methods
    -------
    view_tokens
        Takes a name of tokenization and returns a view of the corpus
        tokenized accordingly. The optional parameter `strings` takes
        a boolean value: True to view string representations of terms;
        False to view integer representations of terms. Default is
        `False`.
    extract_terms
        Static method. Takes an array-like object and returns an
        indexed set of the elements in the object as a 1-D numpy
        array.
    gen_lexicon
        Returns a copy of itself but with `corpus`, `tokens`, and
        `tokens_meta` set to None. Occasionally, the only information
        needed from the Corpus object is the mapping between string
        and integer representations of terms; this provides a smaller
        version of the corpus object for such situations.
    save
        Takes a filename and saves the data contained in a Corpus
        object to a `npy` file using `numpy.savez`.
    load
        Static method. Takes a filename, loads the file data into a
        Corpus object and returns the object
    
    See Also
    --------
    BaseCorpus

    Examples
    --------

    >>> text = ['I', 'came', 'I', 'saw', 'I', 'conquered']
    >>> tok_names = ['sentences']
    >>> tok_data = [[(2, 'Veni'), (4, 'Vidi'), (6, 'Vici')]]

    >>> from vsm.corpus import Corpus
    >>> c = Corpus(text, tok_names=tok_names, tok_data=tok_data)
    >>> c.corpus
    array([0, 3, 0, 2, 0, 1], dtype=int32)
    
    >>> c.terms
    array(['I', 'conquered', 'saw', 'came'],
          dtype='|S9')

    >>> c.terms_int['saw']
    2

    >>> c.view_tokens('sentences')
    [array([0, 3], dtype=int32), array([0, 2], dtype=int32),
     array([0, 1], dtype=int32)]

    >>> c.view_tokens('sentences', strings=True)
    [array(['I', 'came'],
          dtype='|S4'), array(['I', 'saw'],
          dtype='|S3'), array(['I', 'conquered'],
          dtype='|S9')]

    >>> c.view_metadata('sentences')[1]
    'Vidi'
    
    """
    
    def __init__(self,
                 corpus,
                 tok_names=[],
                 tok_data=[]):

        super(Corpus, self).__init__(corpus,
                                     tok_names=tok_names,
                                     tok_data=tok_data,
                                     dtype=np.str_)

        self.__set_terms_int()

        # Integer encoding of a string-type corpus

        self.dtype = np.int32

        self.corpus = np.asarray([self.terms_int[term]
                                  for term in self.corpus],
                                 dtype=self.dtype)



    def __set_terms_int(self):
        """
        Mapping of terms to their integer representations.
        """
        self.terms_int = dict((t,i) for i,t in enumerate(self.terms))


    def view_tokens(self, name, as_strings=False):
        """
        Displays a tokenization of the corpus.

        Parameters
        ----------
        name : string-like
           The name of a tokenization.
        strings : Boolean, optional
            If True, string representations of terms are returned.
            Otherwise, integer representations are returned. Default
            is `False`.

        Returns
        -------
        A tokenized view of `corpus`.

        See Also
        --------
        Corpus
        BaseCorpus
        """
        
        token_list = super(Corpus, self).view_tokens(name)

        if as_strings:

            token_list_ = []

            for token in token_list:

                token = self.terms[token]

                token_list_.append(token)

            return token_list_
            
        return token_list



    @staticmethod
    def load(file):
        """
        Loads data into a Corpus object that has been stored using
        `save`.
        
        Parameters
        ----------
        file : str-like or file-like object
            Designates the file to read. If `file` is a string ending
            in `.gz`, the file is first gunzipped. See `numpy.load`
            for further details.

        Returns
        -------
        A Corpus object storing the data found in `file`.

        See Also
        --------
        Corpus
        Corpus.save
        numpy.load
        """

        print 'Loading corpus from', file

        arrays_in = np.load(file)

        c = Corpus([])

        c.corpus = arrays_in['corpus']

        c.terms = arrays_in['terms']

        c.tok_names = arrays_in['tok_names'].tolist()

        c.tok_data = list()

        for n in c.tok_names:

            t = arrays_in['tok_data_' + n]

            c.tok_data.append(t)

        c.__set_terms_int()

        return c



    def save(self, file):
        """
        Saves data from a Corpus object as an `npz` file.
        
        Parameters
        ----------
        file : str-like or file-like object
            Designates the file to which to save data. See
            `numpy.savez` for further details.
            
        Returns
        -------
        None

        See Also
        --------
        Corpus
        Corpus.load
        numpy.savez
        """
        print 'Saving corpus as', file
        
        arrays_out = dict()
        
        arrays_out['corpus'] = self.corpus
        
        arrays_out['terms'] = self.terms

        arrays_out['tok_names'] = np.asarray(self.tok_names)

        for i,t in enumerate(self.tok_data):

            key = 'tok_data_' + self.tok_names[i]

            arrays_out[key] = t

        np.savez(file, **arrays_out)



    def apply_stoplist(self, stoplist=[], freq=0):
        """
        Takes a Corpus object and returns a copy of it with terms in the
        stoplist removed and with terms of frequency <= `freq1` removed.
        """
        if freq:

            print 'Computing collection frequencies'

            cfs = np.zeros_like(self.terms, dtype=self.corpus.dtype)
    
            for term in self.corpus:

                cfs[term] += 1

            print 'Selecting terms of frequency <=', freq

            freq_stop = np.arange(cfs.size)[(cfs <= freq)]

            stop = set(freq_stop)

        else:

            stop = set()

        for t in stoplist:

            if t in self.terms:

                stop.add(self.terms_int[t])

        if not stop:

            print 'Stop list is empty.'

            return self
    
        print 'Removing stop words'

        f = np.vectorize(lambda x: x not in stop)

        corpus = self.corpus[f(self.corpus)]

        print 'Rebuilding corpus'

        corpus = [self.terms[i] for i in corpus]

        tok_data = []

        for i in xrange(len(self.tok_data)):

            print 'Recomputing token breaks:', self.tok_names[i]

            tokens = self.view_tokens(self.tok_names[i])

            spans = [t[f(t)].size for t in tokens]

            tok = self.tok_data[i].copy()

            tok['idx'] = np.cumsum(spans)

            tok_data.append(tok)

        return Corpus(corpus, tok_data=tok_data, tok_names=self.tok_names)



# MaskedCorpus is now deprecated

class MaskedCorpus(Corpus):
    """
    """
    def __init__(self,
                 corpus,
                 tok_names=[],
                 tok_data=[],
                 masked_terms=None):

        super(MaskedCorpus, self).__init__(corpus,
                                           tok_names=tok_names,
                                           tok_data=tok_data)

        self.corpus = np.ma.array(self.corpus)

        self.terms = np.ma.array(self.terms)

        if masked_terms:

            self.mask_terms(masked_terms)



    def __set_terms_int(self):
        """
        Mapping of terms to their integer representations.
        """

        self.terms_int = dict((t,i) for i,t in enumerate(self.terms.data))


    def mask_terms(self, term_list):
        """

        """
        f = np.vectorize(lambda t: t is np.ma.masked or t in term_list)

        term_mask = f(self.terms)
        
        self.terms = np.ma.masked_where(term_mask, self.terms, copy=False)

        g = np.vectorize(lambda t: t is np.ma.masked or term_mask[t])

        corpus_mask = g(self.corpus)

        self.corpus = np.ma.masked_where(corpus_mask, self.corpus, copy=False)



    @property
    def masked_terms(self):
        """
        """
        v = np.ma.masked_where(np.logical_not(self.terms.mask),
                               self.terms.data, copy=False)

        return v.compressed()



    def view_tokens(self, name, as_strings=False, unmask=False, compress=False):
        """
        Displays a tokenization of the corpus.

        Parameters
        ----------
        name : string-like
           The name of a tokenization.
        as_strings : Boolean, optional
            If True, string representations of terms are returned.
            Otherwise, integer representations are returned. Default
            is `False`.

        Returns
        -------
        A tokenized view of `corpus`.

        See Also
        --------
        MaskedCorpus
        Corpus
        BaseCorpus
        """

        #NB: the references to the original mask do not persist
        #after `numpy.split` (issue in numpy.ma)
        
        token_list = super(Corpus, self).view_tokens(name)

        token_list_ = list()

        for t in token_list:

            # np.split does not cast size 0 arrays as masked arrays. So
            # we'll do it.
            if t.size == 0:

                t = np.ma.array(t)

            if unmask:

                token = t.data

                if as_strings:

                    token = np.array(self.terms[token], dtype=np.str_)

            elif compress:

                token = t.compressed()

                if as_strings:

                    token = np.array(self.terms[token], dtype=np.str_)

            else:

                token = t

                if as_strings:

                    token = np.ma.array(self.terms[token.data],
                                        mask=token.mask,
                                        dtype=np.str_)

            token_list_.append(token)

        return token_list_



    @staticmethod
    def load(file):
        """
        Loads data into a MaskedCorpus object that has been stored using
        `save`.
        
        Parameters
        ----------
        file : str-like or file-like object
            Designates the file to read. If `file` is a string ending
            in `.gz`, the file is first gunzipped. See `numpy.load`
            for further details.

        Returns
        -------
        A MaskedCorpus object storing the data found in `file`.

        See Also
        --------
        MaskedCorpus
        MaskedCorpus.save
        numpy.load
        """

        print 'Loading corpus from', file

        arrays_in = np.load(file)

        c = MaskedCorpus([])

        c.corpus = np.ma.array(arrays_in['corpus_data'])

        c.corpus.mask = arrays_in['corpus_mask']

        c.terms = np.ma.array(arrays_in['terms_data'])

        c.terms.mask = arrays_in['terms_mask']

        c.tok_names = arrays_in['tok_names'].tolist()

        c.tok_data = list()

        for n in c.tok_names:

            t = arrays_in['tok_data_' + n]

            c.tok_data.append(t)

        c.__set_terms_int()

        return c



    def save(self, file):
        """
        Saves data from a MaskedCorpus object as an `npz` file.
        
        Parameters
        ----------
        file : str-like or file-like object
            Designates the file to which to save data. See
            `numpy.savez` for further details.

        Returns
        -------
        None

        See Also
        --------
        MaskedCorpus
        MaskedCorpus.load
        numpy.savez
        """
        print 'Saving masked corpus as', file

        arrays_out = dict()
        
        arrays_out['corpus_data'] = self.corpus.data
        
        arrays_out['corpus_mask'] = self.corpus.mask
        
        arrays_out['terms_data'] = self.terms.data

        arrays_out['terms_mask'] = self.terms.mask

        arrays_out['tok_names'] = np.asarray(self.tok_names)

        for i,t in enumerate(self.tok_data):

            key = 'tok_data_' + self.tok_names[i]

            arrays_out[key] = t

        np.savez(file, **arrays_out)


        
    def to_corpus(self, compress=False):
        """
        Returns a Corpus object containing the data from the
        MaskedCorpus object.
        """
        if compress:

            tok_names = self.tok_names

            tok_data = []

            for name in self.tok_names:

                print 'Realigning tokenization:', name

                print 'Getting tokens:', name

                tokens = self.view_tokens(name)

                print 'Getting metadata:', name
                
                t = self.view_metadata(name).copy()

                print 'Counting unmasked coordinates:', name
            
                spans = [token.count() for token in tokens]

                print 'Computing indices:', name

                indices = np.cumsum(spans)

                t['idx'] = indices
                    
                tok_data.append(t)

            del tokens, t, spans, indices

            print 'Reconstructing string representation of corpus'

            corpus = self.terms[self.corpus.compressed()]

            return Corpus(corpus,
                          tok_names=tok_names,
                          tok_data=tok_data)

        else:

            c = Corpus([])

            c.corpus = self.corpus.data

            c.terms = self.terms.data

            c.terms_int = self.terms_int
            
            c.tok_names = self.tok_names

            c.tok_data = self.tok_data

            return c



def mask_from_stoplist(corp_obj, stoplist):
    """
    Takes a MaskedCorpus object and masks all terms that occur in the
    stoplist. The operation is in-place.
    """
    corp_obj.mask_terms(stoplist)



def mask_from_golist(corp_obj, golist):
    """
    Takes a MaskedCorpus object and masks all terms that do not occur
    in the golist. Does not unmask already masked entries. The
    operation is in-place.
    """
    indices = [corp_obj.terms_int[t] for t in golist if t in corp_obj.terms]
    
    corp_obj.mask_terms(corp_obj.terms[indices])



def mask_freq_t(corp_obj, t):
    """
    Takes a MaskedCorpus object and masks all terms that occur less
    than t times in the corpus. The operation is in-place.
    """
    print 'Computing collection frequencies'

    cfs = np.zeros_like(corp_obj.terms, dtype=corp_obj.corpus.dtype)
    
    for term in corp_obj.corpus.data:

        cfs[term] += 1

    print 'Masking terms of frequency <=', t

    term_list = corp_obj.terms.data[(cfs <= t)]

    corp_obj.mask_terms(term_list)



# Legacy
def mask_f1(corp_obj):
    """
    Takes a MaskedCorpus object and masks all terms that occur only
    once in the corpus. The operation is in-place.
    """

    mask_freq_t(corp_obj, 1)




#
# Testing
#

#TODO: Debug this test
# def test_corpus_conversion():

#     c = random_corpus(10000, 20, 1, 10, metadata=True)

#     mc = c.to_maskedcorpus()

#     cb = mc.to_corpus(compress=False)

#     assert (c.corpus == cb.corpus).all()

#     assert (c.terms == cb.terms).all()

#     assert c.tok_names == cb.tok_names

#     for i in xrange(max(len(c.tok_data), len(cb.tok_data))):

#         assert c.tok_data[i].all() == cb.tok_data[i].all()

#     cbc = mc.to_corpus(compress=True)

#     assert (c.corpus == cbc.corpus).all()

#     assert (c.terms == cbc.terms).all()

#     assert c.tok_names == cbc.tok_names

#     for i in xrange(len(tok_data)):

#         assert c.tok_data[i].all() == cbc.tok_data[i].all()



# def test_compression():

#     c = random_corpus(10000, 20, 1, 10, metadata=True)

#     c = c.to_maskedcorpus()

#     stoplist = [str(np.random.randint(0, 20)) for i in xrange(3)]

#     mask_from_stoplist(c, stoplist)

#     cc = c.to_corpus(compress=True)

#     t1 = c.view_tokens('random', compress=True, as_strings=True)

#     t2 = cc.view_tokens('random', as_strings=True)

#     assert len(t1) == len(t2)

#     for i in xrange(len(t1)):

#         assert t1[i].shape[0] == t2[i].shape[0]

#         assert t1[i].dtype == t2[i].dtype

#         assert (t1[i] == t2[i]).all()


        
# def test_view_tok():

#     c = random_corpus(20, 3, 1, 5, metadata=True)

#     c = c.to_maskedcorpus()

#     mask_from_stoplist(c, ['0'])

#     print c.view_tokens('random', compress=False, as_strings=False)

#     print c.view_tokens('random', compress=True, as_strings=False)

#     print c.view_tokens('random', compress=False, as_strings=True)
    
#     print c.view_tokens('random', compress=True, as_strings=True)

#     return c


    
def test_file():

    c = random_corpus(10000, 500, 1, 20, tok_name='foo', metadata=True)

    c.save('/tmp/foo.npz')

    c_reloaded = c.load('/tmp/foo.npz')

    assert (c.corpus == c_reloaded.corpus).all()

    assert (c.terms == c_reloaded.terms).all()

    assert c.terms_int == c_reloaded.terms_int

    assert c.tok_names == c_reloaded.tok_names
    
    for i in xrange(len(c.tok_data)):
        
        assert (c.tok_data[i] == c_reloaded.tok_data[i]).all()

    return c, c_reloaded
